import csv
import random
import os


INPUT_FILE = "data/raw/chargeback_cases_v2.csv"

TRAIN_FILE = "data/processed/train.csv"
VALIDATION_FILE = "data/processed/validation.csv"
TEST_FILE = "data/test/held_out_test.csv"


random.seed(42)


def load_dataset(filename):
    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)


def save_dataset(rows, filename):

    os.makedirs(os.path.dirname(filename), exist_ok=True)

    if not rows:
        return

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=rows[0].keys()
        )

        writer.writeheader()
        writer.writerows(rows)


def main():

    data = load_dataset(INPUT_FILE)

    print("Total dataset:", len(data))

    random.shuffle(data)

    train = data[:700]
    validation = data[700:850]
    test = data[850:1000]

    save_dataset(train, TRAIN_FILE)
    save_dataset(validation, VALIDATION_FILE)
    save_dataset(test, TEST_FILE)

    print()
    print("Dataset split completed!")
    print("Training cases:", len(train))
    print("Validation cases:", len(validation))
    print("Held-out test cases:", len(test))


if __name__ == "__main__":
    main()