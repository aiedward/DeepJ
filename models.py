# Defines the models used in the experiments

import numpy as np
from keras.layers import Dense, Input, merge, Activation, Dropout, Flatten
from keras.models import Model
from keras.layers.convolutional import Convolution1D
from keras.layers.recurrent import GRU
from util import one_hot
from music import NUM_CLASSES, NOTES_PER_BAR

def note_model(timesteps):
    # TODO Try dropout again?
    note_input = Input(shape=(timesteps, NUM_CLASSES), name='rl/note_input')
    beat_input = Input(shape=(timesteps, NOTES_PER_BAR), name='rl/beat_input')

    x = merge([note_input, beat_input], mode='concat')

    for i in range(2):
        x = GRU(128, return_sequences=True, name='rl/lstm' + str(i))(x)
        x = Activation('relu')(x)

    x = GRU(128, name='rl/lstm_last')(x)
    x = Activation('relu')(x)

    for i in range(2):
        x = Dense(256, name='dense' + str(i))(x)
        x = Activation('relu')(x)

    policy = Dense(NUM_CLASSES, activation='softmax', name='rl/note_policy')(x)
    value = Dense(1, activation='linear', name='rl/value_output')(x)
    return Model([note_input, beat_input], [policy, value])

def note_preprocess(env, x):
    note, beat = x
    return (one_hot(note, NUM_CLASSES), one_hot(beat, NOTES_PER_BAR))

def supervised_model(time_steps):
    # Multi-hot vector of each note
    note_input = Input(shape=(time_steps, NUM_CLASSES), name='note_input')
    beat_input = Input(shape=(time_steps, NOTES_PER_BAR), name='beat_input')

    x = note_input

    x = Dropout(0.2)(x)
    """
    # Conv layer
    for i in range(0):
        x = Convolution1D(64, 8, border_mode='same')(x)
        x = Activation('relu')(x)
        x = Dropout(0.5)(x)
    """

    x = merge([x, beat_input], mode='concat')

    for i in range(2):
        x = GRU(256, return_sequences=True, name='lstm' + str(i))(x)
        x = Activation('relu')(x)
        x = Dropout(0.5)(x)

    x = GRU(256, name='lstm_last')(x)
    x = Activation('relu')(x)
    x = Dropout(0.5)(x)

    for i in range(2):
        x = Dense(256, name='dense' + str(i))(x)
        x = Activation('relu')(x)
        x = Dropout(0.5)(x)

    # Multi-label
    x = Dense(NUM_CLASSES)(x)
    x = Activation('softmax')(x)

    model = Model([note_input, beat_input], x)
    model.compile(optimizer='adam', loss='categorical_crossentropy',
                  metrics=['accuracy'])
    return model
