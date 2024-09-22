from typing import List

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from scipy import stats

from classifier.nn import BaseNN
from classifier.settings import DIFF_WORDS


class PytorchNN(BaseNN):
    def __init__(self, classes: List[str], n_features: int = DIFF_WORDS):
        super().__init__(classes, n_features)
        self._nn = TwoLayerPerceptron(n_features, len(classes)).cuda()
        self.criterion = nn.CrossEntropyLoss()  # Cross-entropy for classification
        self.optimizer = optim.Adam(self._nn.parameters(), lr=0.001)

    def resolve_classes(self, target: List) -> List:
        return [self.classes.index(x) for x in target]

    def one_hot_class(self, class_: str) -> List:
        # classes: ['a', 'b', 'c']
        # 'a' -> [1, 0, 0]; 'c' -> [0, 0, 1]
        ans = [0] * len(self.classes)
        ans[self.classes.index(class_)] = 1
        return ans

    def train(self, text: List[str], target: List):
        x = np.asarray(self.vectorize(text).todense())
        output = self._nn(torch.from_numpy(x).float())
        loss = self.criterion(output, torch.tensor(self.resolve_classes(target), dtype=torch.long).cuda())
        loss.backward()
        self.optimizer.step()
        self.optimizer.zero_grad()

    def infer(self, text: List[str]) -> List:
        x = np.asarray(self.vectorize(text).todense())
        self._nn.eval()
        with torch.no_grad():
            # Forward pass
            y_pred = self._nn.forward(torch.from_numpy(x).float())
        y_pred = y_pred.cpu().numpy()
        return [list(zip(self.classes, r)) for r in y_pred]

    def score(self, text: List[str], target: List):
        x = np.asarray(self.vectorize(text).todense())
        self._nn.eval()
        with torch.no_grad():
            # Forward pass
            y_pred = self._nn.forward(torch.from_numpy(x).float())

        # Convert tensors to numpy arrays for compatibility with sklearn
        y_pred = y_pred.cpu().numpy()

        # Calculate the R2 score
        y_true = np.array([np.array(self.one_hot_class(x)) for x in target])
        r2 = np.average([stats.pearsonr(y_true[x], y_pred[x]).statistic for x in range(y_true.shape[0])])
        return r2


    def save(self, fname: str):
        # Save PyTorch model
        pass

    def load(self, fname: str):
        # Load PyTorch model
        pass

# pylint: disable=R0903
class TwoLayerPerceptron(nn.Module):
    def __init__(self, input_size, output_size, hidden_layer_size=50):
        super().__init__()

        # Define the layers
        self.fc1 = nn.Linear(input_size, hidden_layer_size)  # First layer (input -> hidden)
        self.fc2 = nn.Linear(hidden_layer_size, hidden_layer_size)  # Second layer (hidden -> hidden)
        self.fc3 = nn.Linear(hidden_layer_size, output_size)  # Output layer (hidden -> output)

    def forward(self, x):
        # Pass through the first layer, apply ReLU activation
        x = F.relu(self.fc1(x.cuda()))
        # Pass through the second layer, apply ReLU activation
        x = F.relu(self.fc2(x.cuda()))
        # Output layer (use softmax for multi-class classification)
        x = F.softmax(self.fc3(x.cuda()), dim=1)
        return x
