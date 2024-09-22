from more_itertools import chunked
from sqlalchemy.sql import func

from classifier.main import Classifier
from classifier.models_slim import Post, Source
from classifier.sklearn import SklearnNN as NN

# from classifier.pytorch import PytorchNN as NN

classifier = Classifier(db="tiny.db", from_json="db_tiny.json")
classifier.fill()
classes = classifier.status()["classes"]
# Seems that result depends on classes order. LabelEncoder might help
classes.sort()
print(f"Classes in dataset: {', '.join(classes)}")

# Some very simple and memory-hungry code. Be careful with the big datasets
tasks = (
    classifier.db.query(Post.text, Source.class_)
    .filter(Post.lang == "ru")
    .join(Source)
    .order_by(func.random())
    .all()
)

ds_size = len(tasks)
split_point = int(ds_size * 0.9)
print(
    f"Total text samples: {ds_size}\n"
    f"Train dataset: {split_point}\n"
    f"Test dataset: {ds_size - split_point}\n"
)
train = tasks[:split_point]
test = tasks[split_point:]

x_test = [x[0] for x in test]
y_test = [x[1] for x in test]

nn = NN(classes=classes)

iteration = 0
for chunk in chunked(train * 10, 100):
    iteration += 1
    x_train = [x[0] for x in chunk]
    y_train = [x[1] for x in chunk]
    nn.train(x_train, y_train)
    score = nn.score(x_test, y_test)
    print(f"Step: {iteration:4d} Fit: {score:0.3f}")

print("\nSome examples:")
result = nn.infer(x_test[:10])
for idx in enumerate(result):
    print(x_test[idx[0]])
    for class_ in idx[1]:
        print(f"{class_[0]}: {class_[1]:0.3f}")
    print("-------\n")
