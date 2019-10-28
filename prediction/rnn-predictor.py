
# tutorial from: https://github.com/Hvass-Labs/TensorFlow-Tutorials/blob/master/23_Time-Series-Prediction.ipynb
import csv
import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np
import pandas as pd
import os
from sklearn.preprocessing import MinMaxScaler

# from tf.keras.models import Sequential  # This does not work!
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Input, Dense, GRU, Embedding
from tensorflow.python.keras.optimizers import RMSprop
from tensorflow.python.keras.callbacks import EarlyStopping, ModelCheckpoint, TensorBoard, ReduceLROnPlateau
from tensorflow.python.keras.initializers import RandomUniform

# feito usando python 3.6
FILENAME = '../snapshots/flow-files-with-int-features/fluxo-0-size-102518.5062828064-mb-100.11572879180312-gb.csv'


"""
Plota os dados em um gráfico
"""
# x = []
# y = []
# row_count = 0
# with open(FILENAME,'r') as csvfile:
#     plots = csv.reader(csvfile, delimiter=',')
#     for row in plots:
#         if not row_count == 0:
#             x.append(row_count)
#             # byte_count é indice 9
#             byte_count_gb = float(int(row[9])/1024/1024/1024)
#             y.append(byte_count_gb)
#         row_count = row_count + 1
#
# plt.yticks(np.arange(0, 105, step=10))
# plt.plot(x,y, label='Loaded from file!')
# plt.xlabel('Snapshot counter')
# plt.ylabel('Byte count')
# plt.title('Snapshot counter x byte count')
# plt.legend()
# plt.show()
#


"""
Preprando o modelo
"""
df = pd.read_csv(FILENAME)


print('Preview dos dados:')
print(df.head())

# Temos snapshots a cada 1 segundo. Então, se quiseremos prever o byte_count daqui a 30 segundos, precisamos
# shiftar os dados 30 vezes (30 steps).

shift_steps = 10 # quero prever daqui a 10 steps

# Cria um novo DF com os targets.
# WARNING! You should double-check that you have shifted the data in the right direction!
# We want to predict the future, not the past!
# The shifted data-frame is confusing because Pandas keeps the original time-stamps
# even though we have shifted the data. You can check the time-shift is correct by comparing
# the original and time-shifted data-frames
df_targets = df['byte_count'].shift(-shift_steps)

# remove a feature "byte_count"
# df.drop(['byte_count'], axis=1) # nao funcionou


"""
Separando dados de treinamento de dados de validação
"""
x_data = df.values[0:-shift_steps] # retiramos os ultimos steps (pois é o que queremos prever!)
y_data = df_targets.values[:-shift_steps]


num_data = len(x_data)
train_split = 0.7


num_train = int(train_split * num_data) # This is the number of observations in the training-set
num_test = num_data - num_train # This is the number of observations in the test-set

x_train = x_data[0:num_train]
x_test = x_data[num_train:]

y_train = y_data[0:num_train]
y_test = y_data[num_train:]

num_x_signals = x_data.shape[1] # This is the number of input-signals
num_y_signals = 1 # This is the number of output-signals (valor anterior: y_data.shape[1])

"""
Normalizando dados
"""
x_scaler = MinMaxScaler()
x_train_scaled = x_scaler.fit_transform(x_train)
x_test_scaled = x_scaler.transform(x_test)

# TODO: talvez nao precise criar outro scaler --> avaliar se é necessario
y_scaler = MinMaxScaler()

y_train.shape = (y_train.shape[0], 1)
y_train_scaled = y_scaler.fit_transform(y_train)
y_test_scaled = y_scaler.transform([y_test]) # gambiarra



"""
Data generator

"""
# Instead of training the Recurrent Neural Network on the complete sequences
# observations, we will use the following function to create a batch of shorter
# sub-sequences picked at random from the training-data.
def batch_generator(batch_size, sequence_length):
    """
    Generator function for creating random batches of training-data.
    """

    # Infinite loop.
    while True:
        # Allocate a new array for the batch of input-signals.
        x_shape = (batch_size, sequence_length, num_x_signals)
        x_batch = np.zeros(shape=x_shape, dtype=np.float16)

        # Allocate a new array for the batch of output-signals.
        y_shape = (batch_size, sequence_length, num_y_signals)
        y_batch = np.zeros(shape=y_shape, dtype=np.float16)

        # Fill the batch with random sequences of data.
        for i in range(batch_size):
            # Get a random start-index.
            # This points somewhere into the training-data.
            idx = np.random.randint(num_train - sequence_length)

            # Copy the sequences of data starting at this index.
            x_batch[i] = x_train_scaled[idx:idx+sequence_length]
            y_batch[i] = y_train_scaled[idx:idx+sequence_length]

        yield (x_batch, y_batch)

batch_size = 10
sequence_length = 6 # o que é esse numero ????????????

generator = batch_generator(batch_size=batch_size,
                            sequence_length=sequence_length)

# testando
# x_batch, y_batch = next(generator)


"""
Validation data
"""
validation_data = (np.expand_dims(x_test_scaled, axis=0),
                   np.expand_dims(y_test_scaled, axis=0))




"""
Criando o modelo
"""
model = Sequential()
# We can now add a Gated Recurrent Unit (GRU) to the network. This will have 512
# outputs for each time-step in the sequence.
# Note that because this is the first layer in the model, Keras needs to know
# the shape of its input, which is a batch of sequences of arbitrary length
# (indicated by None), where each observation has a number of input-signals (num_x_signals).
model.add(GRU(units=512,
              return_sequences=True,
              input_shape=(None, num_x_signals,)))

# The GRU outputs a batch of sequences of 512 values.
# The output-signals in the data-set have been limited to be between 0 and 1
# using a scaler-object. So we also limit the output of the neural network using
# the Sigmoid activation function, which squashes the output to be between 0 and 1.
# A problem with using the Sigmoid activation function, is that we can now only output values in the same range as the training-data.
model.add(Dense(num_y_signals, activation='sigmoid'))



# Maybe use lower init-ranges.
init = RandomUniform(minval=-0.05, maxval=0.05)

model.add(Dense(num_y_signals,
                activation='linear',
                kernel_initializer=init))

# We will use Mean Squared Error (MSE) as the loss-function that will be
# minimized. This measures how closely the model's output matches the true output signals.

#However, at the beginning of a sequence, the model has only seen input-signals
# for a few time-steps, so its generated output may be very inaccurate. Using the
# loss-value for the early time-steps may cause the model to distort its later output.
# We therefore give the model a "warmup-period" of 5 time-steps where we don't
# use its accuracy in the loss-function, in hope of improving the accuracy for later time-steps.
warmup_steps = 5


def loss_mse_warmup(y_true, y_pred):
    """
    Calculate the Mean Squared Error between y_true and y_pred,
    but ignore the beginning "warmup" part of the sequences.

    y_true is the desired output.
    y_pred is the model's output.
    """

    # The shape of both input tensors are:
    # [batch_size, sequence_length, num_y_signals].

    # Ignore the "warmup" parts of the sequences
    # by taking slices of the tensors.
    y_true_slice = y_true[:, warmup_steps:, :]
    y_pred_slice = y_pred[:, warmup_steps:, :]

    # These sliced tensors both have this shape:
    # [batch_size, sequence_length - warmup_steps, num_y_signals]

    # Calculate the MSE loss for each value in these tensors.
    # This outputs a 3-rank tensor of the same shape.
    loss = tf.losses.mean_squared_error(labels=y_true_slice,
                                        predictions=y_pred_slice)

    # Keras may reduce this across the first axis (the batch)
    # but the semantics are unclear, so to be sure we use
    # the loss across the entire tensor, we reduce it to a
    # single scalar with the mean function.
    loss_mean = tf.reduce_mean(loss)

    return loss_mean


"""
Compile model
"""
# This is the optimizer and the beginning learning-rate that we will use.
optimizer = RMSprop(lr=1e-3)


# Compila o modelo keras, para depois treiná-lo
model.compile(loss=loss_mse_warmup, optimizer=optimizer)

print('Resumo do modelo:')
print(model.summary())




"""
Callback Functions

"""

# During training we want to save checkpoints and log the progress to TensorBoard so we create the appropriate callbacks for Keras.
# This is the callback for writing checkpoints during training.

path_checkpoint = '23_checkpoint.keras'
callback_checkpoint = ModelCheckpoint(filepath=path_checkpoint,
                                      monitor='val_loss',
                                      verbose=1,
                                      save_weights_only=True,
                                      save_best_only=True)

# This is the callback for stopping the optimization when performance worsens on the validation-set.
callback_early_stopping = EarlyStopping(monitor='val_loss',
                                        patience=5, verbose=1)

# This is the callback for writing the TensorBoard log during training.
callback_tensorboard = TensorBoard(log_dir='./23_logs/',
                                   histogram_freq=0,
                                   write_graph=False)

# This callback reduces the learning-rate for the optimizer if the validation-loss has not improved since the last epoch (as indicated by patience=0). The learning-rate will be reduced by multiplying it with the given factor. We set a start learning-rate of 1e-3 above, so multiplying it by 0.1 gives a learning-rate of 1e-4. We don't want the learning-rate to go any lower than this.
callback_reduce_lr = ReduceLROnPlateau(monitor='val_loss',
                                       factor=0.1,
                                       min_lr=1e-4,
                                       patience=0,
                                       verbose=1)

callbacks = [callback_early_stopping,
             callback_checkpoint,
             callback_tensorboard,
             callback_reduce_lr]


"""
**** Train the Recurrent Neural Network ****

Note that a single "epoch" does not correspond to a single processing of the
training-set, because of how the batch-generator randomly selects sub-sequences
from the training-set. Instead we have selected steps_per_epoch so that one
"epoch" is processed in a few minutes.

Also note that the loss sometimes becomes NaN (not-a-number). This is often
resolved by restarting and running the Notebook again. But it may also be caused
by your neural network architecture, learning-rate, batch-size, sequence-length,
etc. in which case you may have to modify those settings.


--- fit_generator ---
1. Keras calls the generator function supplied to .fit_generator  (in this case, aug.flow ).
2. The generator function yields a batch of size BS  to the .fit_generator  function.
3. The .fit_generator  function accepts the batch of data, performs backpropagation, and updates the weights in our model.
4. This process is repeated until we have reached the desired number of epochs.
"""

## preciso definir o que é o sequence_length para poder usar esse método
# model.fit_generator(
#     generator=generator,
#     epochs=20,
#     steps_per_epoch=100,
#     validation_data=validation_data,
#     callbacks=callbacks
# )


# (np.expand_dims(x_test_scaled, axis=0),
#                    np.expand_dims(y_test_scaled, axis=0))

# usar fit quando todo o dataset cabe na RAM. Usar fit_generator quando não cabe
import ipdb; ipdb.set_trace()
model.fit(
    x=np.expand_dims(x_test_scaled, axis=0),
    y=np.expand_dims(y_test_scaled, axis=0),
    epochs=2,
    verbose=1
)


"""
Load Checkpoint

Because we use early-stopping when training the model, it is possible that the
model's performance has worsened on the test-set for several epochs before
training was stopped. We therefore reload the last saved checkpoint, which
should have the best performance on the test-set.
"""

try:
    model.load_weights(path_checkpoint)
except Exception as error:
    print("Error trying to load checkpoint.")
    print(error)



"""
Performance on Test-Set

"""
# This function expects a batch of data, but we will just use one long
# time-series for the test-set, so we just expand the array-dimensionality
# to create a batch with that one sequence.
result = model.evaluate(x=np.expand_dims(x_test_scaled, axis=0),
                        y=np.expand_dims(y_test_scaled, axis=0))


print("loss (test-set):", result)


# If you have several metrics you can use this instead.
if False:
    for res, metric in zip(result, model.metrics_names):
        print("{0}: {1:.3e}".format(metric, res))





"""
Generate Predictions

"""
