import os
import tensorflow as tf
import numpy as np
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import matplotlib.pyplot as plt
# Caminhos para imagens e máscaras
IMAGE_DIR = 'database/VOC2012_train_val/VOC2012_train_val/JPEGImages/'
MASK_DIR = 'database/VOC2012_train_val/VOC2012_train_val/SegmentationClass/'

IMG_SIZE = (128, 128)  # Redimensionamento das imagens
NUM_CLASSES = 21  # Pascal VOC tem 21 classes (20 + 1 fundo)

def process_mask(mask):
    """Ajusta os valores da máscara para a faixa permitida e aplica one-hot encoding."""
    mask = np.clip(mask, 0, NUM_CLASSES - 1)  # Ajustar valores fora da faixa [0, 20]
    mask = to_categorical(mask, num_classes=NUM_CLASSES)  # One-hot encoding
    return mask

def load_image_mask(image_path, mask_path):
    """Carrega uma imagem e sua máscara correspondente."""
    img = load_img(image_path, target_size=IMG_SIZE)
    mask = load_img(mask_path, target_size=IMG_SIZE, color_mode='grayscale')

    # Converter para arrays NumPy
    img = img_to_array(img) / 255.0  # Normalizar imagem para [0, 1]
    mask = img_to_array(mask).astype(np.int32).squeeze()  # Remover dimensão extra

    # Processar a máscara para garantir que esteja na faixa correta
    mask = process_mask(mask)

    return img, mask

def load_dataset(image_dir, mask_dir):
    """Carrega todas as imagens e máscaras do diretório."""
    images = []
    masks = []

    for filename in os.listdir(image_dir):
        if filename.endswith('.jpg') and os.path.exists(os.path.join(image_dir, filename)) and os.path.exists(os.path.join(mask_dir, filename.replace('.jpg', '.png'))):
            img_path = os.path.join(image_dir, filename)
            mask_path = os.path.join(mask_dir, filename.replace('.jpg', '.png'))

            # Carregar imagem e máscara
            img, mask = load_image_mask(img_path, mask_path)
            images.append(img)
            masks.append(mask)

    return np.array(images), np.array(masks)

# Carregar as imagens e máscaras
X, Y = load_dataset(IMAGE_DIR, MASK_DIR)
print(f"Dataset carregado: {X.shape} imagens, {Y.shape} máscaras")

def plot_and_save(history, metric, save_path):
    """Gera e salva um gráfico da métrica fornecida."""
    plt.figure()
    
    # Plotar os dados de treino e validação
    plt.plot(history.history[metric], label=f'Train {metric}')
    plt.plot(history.history[f'val_{metric}'], label=f'Val {metric}')
    
    plt.title(f'{metric.capitalize()} over Epochs')
    plt.xlabel('Epochs')
    plt.ylabel(metric.capitalize())
    plt.legend()
    
    # Salvar o gráfico
    plt.savefig(save_path)
    plt.close()  # Fechar para liberar memória



# Definir o modelo U-Net para segmentação semântica
def unet_model(input_size=(128, 128, 3), num_classes=21):
    inputs = tf.keras.Input(input_size)

    # Encoder
    c1 = tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same')(inputs)
    p1 = tf.keras.layers.MaxPooling2D((2, 2))(c1)

    c2 = tf.keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same')(p1)
    p2 = tf.keras.layers.MaxPooling2D((2, 2))(c2)

    # Bottleneck
    bn = tf.keras.layers.Conv2D(256, (3, 3), activation='relu', padding='same')(p2)

    # Decoder
    u1 = tf.keras.layers.UpSampling2D((2, 2))(bn)
    d1 = tf.keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same')(u1)

    u2 = tf.keras.layers.UpSampling2D((2, 2))(d1)
    outputs = tf.keras.layers.Conv2D(num_classes, (1, 1), activation='softmax')(u2)

    model = tf.keras.Model(inputs, outputs)
    return model

# Compilar o modelo
model = unet_model()
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Treinamento
history = model.fit(X, Y, batch_size=8, epochs=25, validation_split=0.1)
# Gerar e salvar os gráficos de Loss e Accuracy
plot_and_save(history, 'loss', 'loss_plot.png')
plot_and_save(history, 'accuracy', 'accuracy_plot.png')
model.save('unet_model.h5')
