import numpy as np


class MLP:
    " Multi-layer perceptron "

    def __init__(self, sizes, beta=1, momentum=0.9):

        """
        sizes is a list of length four. The first element is the number of features 
                in each samples. In the MNIST dataset, this is 784 (28*28). The second 
                and the third  elements are the number of neurons in the first 
                and the second hidden layers, respectively. The fourth element is the 
                number of neurons in the output layer which is determined by the number 
                of classes. For example, if the sizes list is [784, 5, 7, 10], this means 
                the first hidden layer has 5 neurons and the second layer has 7 neurons. 

        beta is a scalar used in the sigmoid function
        momentum is a scalar used for the gradient descent with momentum
        """
        self.beta = beta
        self.momentum = momentum

        self.nin = sizes[0]  # number of features in each sample
        self.nhidden1 = sizes[1]  # number of neurons in the first hidden layer
        self.nhidden2 = sizes[2]  # number of neurons in the second hidden layer
        self.nout = sizes[3]  # number of classes / the number of neurons in the output layer

        # Initialise the network of two hidden layers
        self.weights1 = (np.random.rand(self.nin + 1, self.nhidden1) - 0.5) * 2 / np.sqrt(self.nin)  # hidden layer 1
        self.weights2 = (np.random.rand(self.nhidden1 + 1, self.nhidden2) - 0.5) * 2 / np.sqrt(
            self.nhidden1)  # hidden layer 2
        self.weights3 = (np.random.rand(self.nhidden2 + 1, self.nout) - 0.5) * 2 / np.sqrt(
            self.nhidden2)  # output layer

    def train(self, inputs, targets, eta, niterations):
        """
        inputs is a numpy array of shape (num_train, D) containing the training images
                    consisting of num_train samples each of dimension D.

        targets is a numpy array of shape (num_train, D) containing the training labels
                    consisting of num_train samples each of dimension D.

        eta is the learning rate for optimization
        niterations is the number of iterations for updating the weights

        """
        ndata = np.shape(inputs)[0]  # number of data samples
        # adding the bias
        inputs = np.concatenate((inputs, -np.ones((ndata, 1))), axis=1)

        # numpy array to store the update weights
        updatew1 = np.zeros((np.shape(self.weights1)))
        updatew2 = np.zeros((np.shape(self.weights2)))
        updatew3 = np.zeros((np.shape(self.weights3)))

        for n in range(niterations):

            #############################################################################
            # TODO: implement the training phase of one iteration which consists of two phases:
            # the forward phase and the backward phase. you will implement the forward phase in
            # the self.forwardPass method and return the outputs to self.outputs. Then compute
            # the error (hints: similar to what we did in the lab). Next is to implement the
            # backward phase where you will compute the derivative of the layers and update
            # their weights.
            #############################################################################

            # forward phase
            self.outputs = self.forwardPass(inputs)

            # Error using the sum-of-squares error function
            error = 0.5 * np.sum((self.outputs - targets) ** 2)

            if (np.mod(n, 100) == 0):
                print("Iteration: ", n, " Error: ", error)

            # backward phase
            # Compute the derivative of the output layer. NOTE: you will need to compute the derivative of
            # the softmax function. Hints: equation 4.55 in the book.

            hOutput = self.hidden2.dot(self.weights3)
            dErrorWithRespectToHOutput = self.softmaxDerivative(hOutput) * (self.outputs - targets) 
            deltao = self.hidden2.T.dot(dErrorWithRespectToHOutput)

            # compute the derivative of the second hidden layer

            hHidden2 = self.hidden1.dot(self.weights2)
            dErrorWithRespectToHidden2 = dErrorWithRespectToHOutput.dot(self.weights3.T)
            dErrorWithRespectToHHidden2 = self.sigmoidDerivative(hHidden2) * dErrorWithRespectToHidden2[:, :-1]
            deltah2 = self.hidden1.T.dot(dErrorWithRespectToHHidden2)

            # compute the derivative of the first hidden layer

            hHidden1 = inputs.dot(self.weights1)
            dErrorWithRespectToHidden1 = dErrorWithRespectToHHidden2.dot(self.weights2.T)
            dErrorWithRespectToHHidden1 = self.sigmoidDerivative(hHidden1) * dErrorWithRespectToHidden1[:, :-1]
            deltah1 = inputs.T.dot(dErrorWithRespectToHHidden1)

            # update the weights of the three layers: self.weights1, self.weights2 and self.weights3
            # here you can update the weights as we did in the week 4 lab (using gradient descent)
            # but you can also add the momentum

            # Calculating momentum to add on by using the update of the previous iteration
            momentumw1 = self.momentum * updatew1
            momentumw2 = self.momentum * updatew2
            momentumw3 = self.momentum * updatew3

            updatew1 = eta * deltah1 + momentumw1
            updatew2 = eta * deltah2 + momentumw2
            updatew3 = eta * deltao  + momentumw3

            self.weights1 -= updatew1
            self.weights2 -= updatew2
            self.weights3 -= updatew3
            #############################################################################
            # END of YOUR CODE
            #############################################################################

    def forwardPass(self, inputs):
        """
            inputs is a numpy array of shape (num_train, D) containing the training images
                    consisting of num_train samples each of dimension D.
        """
        #############################################################################
        # TODO: Implement the forward phase of the model. It has two hidden layers
        # and the output layer. The activation function of the two hidden layers is
        # sigmoid function. The output layer activation function is the softmax function
        # because we are working with multi-class classification.
        #############################################################################

        ndata = inputs.shape[0]

        # layer 1
        # compute the forward pass on the first hidden layer with the sigmoid function

        self.hidden1 = self.sigmoid(inputs.dot(self.weights1))
        # Add the bias inputs for use in the next layer
        self.hidden1 = np.concatenate((self.hidden1, -np.ones((ndata, 1))), axis=1)

        # layer 2
        # compute the forward pass on the second hidden layer with the sigmoid function

        self.hidden2 = self.sigmoid(self.hidden1.dot(self.weights2))
        # Add the bias inputs for use in the next layer
        self.hidden2 = np.concatenate((self.hidden2, -np.ones((ndata, 1))), axis=1)

        # output layer
        # compute the forward pass on the output layer with softmax function

        outputs = self.softmax(self.hidden2.dot(self.weights3))

        #############################################################################
        # END of YOUR CODE
        #############################################################################
        return outputs

    def evaluate(self, X, y):
        """
            this method is to evaluate our model on unseen samples
            it computes the confusion matrix and the accuracy

            X is a numpy array of shape (num_train, D) containing the testing images
                    consisting of num_train samples each of dimension D.
            y is  a numpy array of shape (num_train, D) containing the testing labels
                    consisting of num_train samples each of dimension D.
        """

        inputs = np.concatenate((X, -np.ones((np.shape(X)[0], 1))), axis=1)
        outputs = self.forwardPass(inputs)
        nclasses = np.shape(y)[1]

        # 1-of-N encoding
        outputs = np.argmax(outputs, 1)
        targets = np.argmax(y, 1)

        cm = np.zeros((nclasses, nclasses))
        for i in range(nclasses):
            for j in range(nclasses):
                cm[i, j] = np.sum(np.where(outputs == i, 1, 0) * np.where(targets == j, 1, 0))

        print("The confusion matrix is:")
        print(cm)
        print("The accuracy is ", np.trace(cm) / np.sum(cm) * 100)

        return cm

    def sigmoid(self, x):
      return 1.0 / (1.0 + np.exp(-self.beta * x))

    def sigmoidDerivative(self, x):
      return self.beta * self.sigmoid(x) * (1.0 - self.sigmoid(x))

    def softmax(self, x):
      return np.exp(x) / (np.exp(x).sum(axis=1, keepdims=True))

    def softmaxDerivative(self, x):
      return self.softmax(x) * (1.0 - self.softmax(x))
