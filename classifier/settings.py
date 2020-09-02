DIFF_WORDS = 2 ** 18  # nn input layer width
BATCH_SIZE = 100  # nn coefficients are recalculated after passing batch_Size samples
DEBUG = True  # make it False to test it locally on small dataset

if DEBUG:
    # размер валидационной/тестовой выборки
    VAL_SIZE = 10
    DB_LIMIT = "LIMIT 50"  # cutoff dataset for testing purposes
    # колько бачей за одну эпоху обучения (у нас 2 или 3, одна эпоха - это все тексты из выборки увидены нейросетью 1 раз)
    STEPS_PER_EPOCH = 10
else:
    VAL_SIZE = 10000  # validation dataset size in samples
    DB_LIMIT = ""
    STEPS_PER_EPOCH = 470  # should be approx. total_samples/batch_size
    # corpus consists of approx. 57k of samples. It seems good to take 10k for validation and 47k for training
