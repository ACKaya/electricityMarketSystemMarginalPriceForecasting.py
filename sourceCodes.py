# Gerekli kütüphaneleri yükleyin
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM
from datetime import datetime
# Veriyi yükleyin
file_path = "C:\\Users\\pc\\Desktop\\ack.csv"
data = pd.read_csv(file_path, delimiter=';', skiprows=1, names=["Tarih", "SMF"])

# Tarih sütununu datetime formatına çevirin
data['Tarih'] = pd.to_datetime(data['Tarih'], format='%d.%m.%Y')
data['SMF'] = data['SMF'].str.replace(',', '.').astype(float)

# Tarih sütununu indeks olarak ayarlayın
data.set_index('Tarih', inplace=True)
# Veriyi normalize edin
scaler = MinMaxScaler(feature_range=(0, 1))
data['SMF'] = scaler.fit_transform(data[['SMF']])

# Eğitim ve test setlerini oluşturun
train_data = data[:'2022']
test_data = data['2023':]

# Veriyi zaman serisi formatına uygun hale getirin
def create_dataset(dataset, time_step=1):
    dataX, dataY = [], []
    for i in range(len(dataset)-time_step-1):
        a = dataset[i:(i+time_step), 0]
        dataX.append(a)
        dataY.append(dataset[i + time_step, 0])
    return np.array(dataX), np.array(dataY)

# Zaman adımı
time_step = 24

# Eğitim verisini hazırlayın
train_data = train_data.values
X_train, y_train = create_dataset(train_data, time_step)

# Test verisini hazırlayın
test_data = test_data.values
X_test, y_test = create_dataset(test_data, time_step)

# Veriyi LSTM formatına uygun hale getirin
X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)

# Modeli oluşturun
model = Sequential()
model.add(LSTM(50, return_sequences=True, input_shape=(time_step, 1)))
model.add(LSTM(50, return_sequences=False))
model.add(Dense(1))
model.compile(optimizer='adam', loss='mean_squared_error')

# Modeli eğitin
model.fit(X_train, y_train, epochs=100, batch_size=64, validation_data=(X_test, y_test), verbose=1)

# Tahmin yapın
train_predict = model.predict(X_train)
test_predict = model.predict(X_test)

# Tahminleri geri ölçeklendirin
train_predict = scaler.inverse_transform(train_predict)
test_predict = scaler.inverse_transform(test_predict)
y_train = scaler.inverse_transform([y_train])
y_test = scaler.inverse_transform([y_test])

# Grafik çizimi
plt.figure(figsize=(14, 8))
plt.plot(data.index, scaler.inverse_transform(data[['SMF']]), label="Gerçek Değerler")
train_predict_plot = np.empty_like(data[['SMF']])
train_predict_plot[:, :] = np.nan
train_predict_plot[time_step:len(train_predict)+time_step, :] = train_predict
plt.plot(data.index, train_predict_plot, label="Eğitim Tahminleri")
test_predict_plot = np.empty_like(data[['SMF']])
test_predict_plot[:, :] = np.nan
test_predict_plot[len(train_predict)+(time_step*2)+1:len(data)-1, :] = test_predict
plt.plot(data.index, test_predict_plot, label="Test Tahminleri")
plt.xlabel("Tarih")
plt.ylabel("SMF")
plt.legend()
plt.show()
