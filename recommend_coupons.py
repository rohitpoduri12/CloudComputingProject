
from __future__ import print_function
import sys

import boto3
from boto3.dynamodb.conditions import Key
import boto
import sys, os
from boto.s3.key import Key
from time import sleep
from pyspark import SparkContext
from pyspark.mllib.recommendation import ALS,MatrixFactorizationModel, Rating
from math import sqrt


ACCESS_KEY_2 = ""
SECRET_KEY_2 = ""

stdin, stdout = sys.stdin, sys.stdout
reload(sys)
sys.stdin, sys.stdout = stdin, stdout
sys.setdefaultencoding('utf-8')
if __name__=="__main__":
    if len(sys.argv)!=2:
        print ("Usage: Path-to-test.py <path-to-file>")
        exit(-1)
    sc = SparkContext(appName="Coupons")
    sc.setLogLevel("ERROR")
    load_data = sc.textFile("s3a://ccfinalproject/ratings_1_1.txt")
    split_data = load_data.map(lambda l: l.split(','))
    
    ratings = split_data.map(lambda x: Rating(int(x[0]),int(x[1]), float(x[2])))
    
    train, test = ratings.randomSplit([0.7,0.3],7856)
   
    rank = 10
    lmbda = 0.1
    numIterations = 10
    model = ALS.train(train, rank, numIterations, lmbda)
    
    print('For User Y, N Products to Promote')
    recommendations = model.recommendProducts(int(sys.argv[1]),10)
    print(recommendations)

    table = dynamodb.Table('recommendations')
    
    for i in range(0,len(recommendations)):
        table.put_item(
               Item={
                   'UserId': str(recommendations[i].user),
                   'coupon_Id': str(recommendations[i].product),
                   'rating': str(recommendations[i].rating),
                'timestamp': "###"
                       }
            )
    
    pred_input = train.map(lambda x:(x[0],x[1]))
    pred = model.predictAll(pred_input)
    
    true_reorg = train.map(lambda x:((x[0],x[1]), x[2]))
    pred_reorg = pred.map(lambda x:((x[0],x[1]), x[2]))
    true_pred = true_reorg.join(pred_reorg)
    
    MSE = true_pred.map(lambda r: (r[1][0] - r[1][1])**2).mean()
    print ('square root the Mean-Squared Error: Train')
    print (sqrt(MSE))
    
    test_input = test.map(lambda x:(x[0],x[1])) 
    pred_test = model.predictAll(test_input)
    test_reorg = test.map(lambda x:((x[0],x[1]), x[2]))
    pred_reorg = pred_test.map(lambda x:((x[0],x[1]), x[2]))
    test_pred = test_reorg.join(pred_reorg)
    test_MSE = test_pred.map(lambda r: (r[1][0] - r[1][1])**2).mean()
    print ('square root the Mean-Squared Error: Test')
    test_RMSE = sqrt(test_MSE)
    print(test_RMSE)
    
    sc.stop()
    
    
    
    
    
