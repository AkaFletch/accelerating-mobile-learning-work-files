#!/usr/bin/env python3
import urllib.request
import argparse
import subprocess
import time
from os import listdir
from getSyn import findSyn

parser = argparse.ArgumentParser(description="will test a given pb using label_images")
parser.add_argument('--graph', metavar='store', type=str, help='the .pb file you wish to test')
parser.add_argument('--output_layer', metavar='store',type=str, help='the output layer of the graph')
parser.add_argument('--raw_data_dir', metavar='store', type=str, help='the directory with all the raw data')
parser.add_argument('--labels', metavar='store', type=str, help='the path to the labels.txt')
parser.add_argument('--image_width', metavar='store', type=str, default='299', help='width of the image in px')
parser.add_argument('--image_height', metavar='store', type=str, default='299', help='height of the image in px')
parser.add_argument('--graph_name', metavar='store', type=str, help='name of the model')
parser.add_argument('--output', metavar='store', type=str, help='output dir')
parser.add_argument('--startAt', metavar='store', type=str, help='which category to start at', default=0)

args = parser.parse_args()
if int(args.startAt) > 0:
    f = open(args.output, "a")
else:
    f = open(args.output, "w")


def getLabelFromSys(sysLabel):
    return findSyn(sysLabel)

def getDirectories(directory):
    return listdir(directory)

def testImage(label, image, num):
    command="/home/matt/Documents/University/project/tensorflow/bazel-bin/tensorflow/examples/label_image/label_image"
    command = command + " --image=" + image
    command = command + " --graph=" + args.graph
    command = command + " --output_layer=" + args.output_layer
    command = command + " --labels=" + args.labels
    command = command + " --input_width=" + args.image_width
    command = command + " --input_height=" + args.image_height
    
    start = time.time()
    tensorflow = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    tensorflow.wait()
    tensorflow.stdout.readline()
    end = time.time()
	
    timer = end-start
    top = str(tensorflow.stdout.readline()).rstrip()
    if label in top:
        return [1, 1, timer]
    else:
        for i in range(4):
            top = str(tensorflow.stdout.readline()).rstrip()
            if label in top:
                return [0, 1, timer]
    return [0,0, timer]


def testAccuracyOfCategory(directory, label):
    f.write("Testing accuracy of " + label + " category")
    f.write("\n")
    top1 = 0
    top5 = 0
    timer = 0
    count = 0;
    dirList = getDirectories(directory)
    amount = len(dirList)-30
    for i in dirList[0:20]:
        result = testImage(label, directory + '/' + i, count)
        top1 = top1 + result[0]
        top5 = top5 + result[1]
        timer = timer + result[2]
        count = count + 1
    f.write("Top 1 on " + label + ":" + str(top1) + "/" + str(amount) + ": " + str(top1/amount))
    f.write("\n")
    f.write("Top 5 on " + label + ":" + str(top5) + "/" + str(amount) + ": " + str(top5/amount))
    f.write("\n")
    f.write("Time Average on " + label + ":" + str(timer/amount))
    f.write("\n")
    vals = [top1, top5, amount, timer]
    return vals

dirs = getDirectories(args.raw_data_dir)
top1 = 0
top5 = 0
amount = 0
count = int(args.startAt)
timer = 0
print("Starting")
for i in dirs[int(args.startAt):1000]:
    vals = testAccuracyOfCategory(args.raw_data_dir + "/" + i, getLabelFromSys(i))
    top1 = top1 + vals[0]
    top5 = top5 + vals[1]
    amount = amount + vals[2]
    timer = timer + vals[3]
    count = count + 1
    print("Category " + str(count) + "/1000. Estimated time remaining: " + str((timer/(count-int(args.startAt)))*((1000-(count)))))

if int(args.startAt) == 0:
    f.write("Top 1:" + str(top1) + "/" + str(amount) + ": " + str(top1/amount))
    f.write("\n")
    f.write("Top 5:" + str(top5) + "/" + str(amount) + ": " + str(top5/amount))
    f.write("\n")
f.close()

if int(args.startAt) != 0:
    f = open(args.output, "r")
    readLine = f.readline()
    top1 = 0
    top5 = 0
    parity = 0
    total = 0
    for i in f:
        i = i.rstrip()
        if  "on" in i and "Average" not in i and "Testing" not in i:
            if parity == 0:
                top1 = top1 + int(i.split(':')[1].split('/')[0])
                parity = 1
                total = total + 0.5 * 20
            elif parity == 1:
                top5 = top5 + int(i.split(':')[1].split('/')[0])
                parity = 0
                total = total + 0.5 * 20

    f.close()
    f = open(args.output, "a")
    f.write("Top 1:" + str(top1) + "/" + str(total) + ": " + str(top1/total))
    f.write("\n")
    f.write("Top 5:" + str(top5) + "/" + str(total) + ": " + str(top5/total))
    f.write("\n")
