import numpy as np
import pandas as pd

def polynomialKernel(X, Y, polyDegree):
    m1,_ = X.shape
    m2,_ = Y.shape
    K = np.zeros((m1, m2))
    for i in range(m1):
        for j in range(m2):
            #print(i,j)
            K[i,j] = (1 + np.dot(X[i].T, Y[j])) ** polyDegree
    return K

def shuffling(x,y):
    df = pd.DataFrame(x)
    df['label'] = y
    df = df.sample(frac=1).reset_index(drop=True) # shuffling
    y = df.label
    x = df.drop(['label'], axis=1)

    return x,y


# kernel perceptron is one perceptron - multi class kernel perceptron append all the kernel perceptrons
class KernelPerceptron():
    def __init__(self, classLabel, epochNumber, polynomialDegree):
        self.classLabel = classLabel # label for the specific classifier
        self.epochNumber = epochNumber
        self.polynomialDegree = polynomialDegree
        self.interim = int(self.epochNumber/5)


    # Training Algorithm Perceptron
    def train(self, xTrain, yTrain, kernelTrain):
        print("... training classifier {0} ...".format(self.classLabel))

        # Setting training variables
        nSamples, _ = xTrain.shape
        alpha = np.zeros(nSamples)
        yTrain = self.classify(yTrain) # highlight the same labels as the current perceptron (1 if labels corresponds, or -1)

        error = 0
        alphaMin = np.zeros(nSamples)
        errorMin = nSamples

        self.average = np.zeros(self.interim)
        self.smallestErr = np.zeros((nSamples,self.interim))
        self.alphaCounters = []
        self.supportVectors = []

        for epoch in range(1,self.epochNumber+1): # given number of epochs

            # This is ONE EPOCH - a full cycle through data (each training point)
            for t in range(nSamples):
                # Predicting
                yHat = 1 if np.sum(alpha*yTrain*kernelTrain[:2000,t]) > 0 else -1
                # Updating weights
                if yHat != yTrain[t]:
                    alpha[t] += 1

            error = np.sum(alpha) / (nSamples*epoch)
            if error < errorMin:
                errorMin = error
                alphaMin = alpha

            if epoch%5 == 0:
                # predictors average
                self.average[int(epoch/5-1)] = round(np.sum(alpha) / (nSamples*epoch),2)
                # predictor achieving the smallest training error
                self.smallestErr[:,int(epoch/5-1)] = alphaMin
                self.alphaCounters.append(alphaMin[np.nonzero(alphaMin)])
                self.supportVectors.append(xTrain[np.nonzero(alphaMin)])

        # Non zero weights and corresponding training image stored in object
        #self.alphaCounters = alphaMin[np.nonzero(alphaMin)]
        #self.supportVectors = xTrain[np.nonzero(alphaMin)]

    def predict(self, xTest, yTest):
        print("... predicting with perceptron {0} ...".format(self.classLabel))
        # Calculating kernel matrix
        kernelTest = []
        for i in range(len(self.supportVectors)):
            kernelTest.append(polynomialKernel(self.supportVectors[i], xTest.values, self.polynomialDegree))

        # Calculating predicted y
        nSamples = len(xTest)
        predictions = np.zeros((2,self.interim,nSamples))

        for t in range(nSamples):
            for i in range(self.interim):
                # predictions using predictors average
                predictions[0,i,t] = np.sum(self.average[i]*kernelTest[i][:,t])
                # predictions using predictor achieving the smallest training error
                predictions[1,i,t] = np.sum(self.alphaCounters[i]*kernelTest[i][:,t]) # use smallestErr!!!!

        return predictions

    def classify(self, labels): # confronta le etichette con quelle che dovrebbero essere corrette, cioe quelle della classe (?)
        return np.where(labels == self.classLabel, 1, -1) # where assign 1 or -1 based on the condition (first parameter)
