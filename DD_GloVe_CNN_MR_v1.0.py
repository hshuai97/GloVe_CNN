from numpy import asarray
from numpy import zeros
import numpy as np
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Flatten
from keras.layers import Embedding
from keras.layers.convolutional import Conv1D
from keras.layers.convolutional import MaxPooling1D
from keras.utils.vis_utils import plot_model
from sklearn.model_selection import train_test_split
import time
from Text_Preprocess.TextPreprocess import *

start = time.process_time()
##############################################################################
path_neg = "D:\SoftPackage\pycharm\PyCharmProject\MachineLearning\Data\MR_v1.0_processed\\neg_processed.txt"
path_pos = "D:\SoftPackage\pycharm\PyCharmProject\MachineLearning\Data\MR_v1.0_processed\pos_processed.txt"
##############################################################################
# 读取数据
file_neg = open(path_neg, 'r', encoding='utf-8')
neg_comments = file_neg.readlines()
file_neg.close()

file_pos = open(path_pos, 'r', encoding='utf-8')
pos_comments = file_pos.readlines()
file_pos.close()
##############################################################################
# Let's have a look at the neg_comments and postive_comments
print(f"Example of pos_comments: {pos_comments[:4]}")
print(f"Example of neg_comments: {neg_comments[:4]}")
print(f"len pos comments: {len(pos_comments)}")
print(f"len neg comments: {len(neg_comments)}")
##############################################################################
# initilize the text preprocessor class object
comment_text_processor = Text_Preprocess()

# process the positive and negative comments
processed_pos_comments = comment_text_processor.preprocess(pos_comments)
processed_neg_comments = comment_text_processor.preprocess(neg_comments)
# Let's have a look at the processed data information
print("Example of Positive comments:{}".format(pos_comments[:4]))
print("Example of processed Positive comments:{}\n".format(processed_pos_comments[:4]))
print(f"len processed pos comments: {len(processed_pos_comments)}")
print(f"len processed neg comments: {len(processed_neg_comments)}")
##############################################################################
docs = processed_pos_comments + processed_neg_comments

labels = [1 for i in range(len(processed_pos_comments))]
labels.extend([0 for i in range(len(processed_neg_comments))])

labels = np.array(labels)
##############################################################################
# prepare tokenizer
t = Tokenizer()
t.fit_on_texts(docs)
vocab_size = len(t.word_index) + 1
print(f"vocab_size: {vocab_size}")

##############################################################################
# integer encode the documents
encoded_docs = t.texts_to_sequences(docs)
print(f"encoded_docs: {encoded_docs[:4]}")
##############################################################################
# pad documents to a max length of n words
# max_length = max([len(s.split()) for s in docs])
max_length = max([len(docs[i]) for i in range(len(docs))])
print(f"max_length: {max_length}")
padded_docs = pad_sequences(encoded_docs, maxlen=max_length, padding='post')
print(f"padded_doc:\n {padded_docs[:4]}")
##############################################################################
# 划分train and test set
# note: random_state让每次划分的训练集和数据集相同
X_train, X_test, y_train, y_test = train_test_split(padded_docs, labels, test_size=0.2,random_state=100)
##############################################################################
path_glove = "D:\SoftPackage\pycharm\PyCharmProject\MachineLearning\Data\glove.6B.100d.txt"
# load the whole embedding into memory
embeddings_index = dict()
f = open(path_glove, mode='rt', encoding='utf-8')
for line in f:
    values = line.split()
    word = values[0]
    coefs = asarray(values[1:], dtype='float32')
    embeddings_index[word] = coefs
f.close()
print('Loaded %s GloVe word vectors.' % len(embeddings_index))
##############################################################################
# create a weight matrix for words in training docs
embedding_matrix = zeros((vocab_size, 100))
for word, i in t.word_index.items():
    embedding_vector = embeddings_index.get(word)
    if embedding_vector is not None:
        embedding_matrix[i] = embedding_vector
##############################################################################
# define model
model = Sequential()
e = Embedding(vocab_size, 100, weights=[embedding_matrix], input_length=max_length, trainable=False)

model.add(e)
model.add(Conv1D(filters=32, kernel_size=8, activation='relu'))
model.add(MaxPooling1D(pool_size=2))
model.add(Flatten())
model.add(Dense(10, activation="relu"))
# model.add(Dense(100, activation='relu'))
model.add(Dense(1, activation='sigmoid'))
##############################################################################
# compile the model
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['acc'])
# summarize the model
model.summary()
to_file = "D:\SoftPackage\pycharm\PyCharmProject\MachineLearning\Data\\Model_png\\Glove_CNN_MRv1.0.png"
plot_model(model, to_file= to_file, show_shapes=True)
##############################################################################
# fit the model
model.fit(X_train, y_train, epochs=10, verbose=1)
##############################################################################
# evaluate the model
loss, acc = model.evaluate(X_train, y_train, verbose=0)
print('train accuracy: %f' % (acc*100))

_, accuracy = model.evaluate(X_test, y_test, verbose=0)
print('test accuracy: %f' % (accuracy*100))

end = time.process_time()
print(f"running time: {end-start}")
