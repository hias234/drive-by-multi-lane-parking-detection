class DataSet:
    def __init__(self, class_labels):
        self.x = []
        self.y_true = []
        self.class_labels = class_labels

    def append_sample(self, x, y_true):
        self.x.append(x)
        self.y_true.append(y_true)