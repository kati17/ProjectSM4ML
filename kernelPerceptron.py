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
        self.statistics = np.zeros((2,self.interim))

    # Training Algorithm Perceptron
    def train(self, xTrain, yTrain, kernelTrain):
        print("... training classifier {0} ...".format(self.classLabel))

        # Setting training variables
        nSamples, _ = xTrain.shape
        alpha = np.zeros(nSamples)
        error = np.zeros(nSamples)
        y = yTrain
        yTrain = self.classify(yTrain) # highlight the same labels as the current perceptron (1 if labels corresponds, or -1)


        for epoch in range(1,self.epochNumber+1): # given number of epochs

            # This is ONE EPOCH - a full cycle through data (each training point)
            for t in range(nSamples):
                # Predicting
                yPred = np.sum(alpha*yTrain*kernelTrain[:,t])
                #print(yPred)
                yHat = 1 if yPred > 0 else -1
                #print(yTrain[t]) # 1 or -1

                # Updating weights
                if yHat != yTrain[t]:
                    alpha[t] += 1

                error[t] += y[t] - yPred
                #print(error)


            if epoch%5 == 0:
                # predictors average
                self.statistics[0,int(epoch/5-1)] = round(np.sum(alpha) / (nSamples*epoch),2)
                # predictor achieving the smallest training error
                index = np.argmin(error)
                #print(index)
                self.statistics[1,int(epoch/5-1)] = alpha[index] # ma ha senso come valore?

        #print(self.statistics)

        # Non zero weights and corresponding training image stored in object
        #self.alphaCounters = alpha[np.nonzero(alpha)]
        self.supportVectors = xTrain[np.nonzero(alpha)]

    def predict(self, xTest, yTest):
        print("... predicting with perceptron {0} ...".format(self.classLabel))
        # Calculating kernel matrix
        kernelTest = polynomialKernel(self.supportVectors, xTest.values, self.polynomialDegree)
        #print(kernelTest)

        # Calculating predicted y
        nSamples = kernelTest.shape[1]
        predictions = np.zeros((2,self.interim,nSamples))
        #pred = np.zeros(nSamples)

        for t in range(nSamples):
            #pred[t] = np.sum(self.alphaCounters*kernelTest[:,t]) # this is the prediction
            for i in range(self.interim):
                # predictions using predictors average
                predictions[0,i,t] = np.sum(self.statistics[0,i]*kernelTest[:,t])
                # predictions using predictor achieving the smallest training error
                predictions[1,i,t] = np.sum(self.statistics[1,i]*kernelTest[:,t])
        #print(predictions)

        return predictions

    def classify(self, labels): # confronta le etichette con quelle che dovrebbero essere corrette, cioe quelle della classe (?)
        return np.where(labels == self.classLabel, 1, -1) # where assign 1 or -1 based on the condition (first parameter)
