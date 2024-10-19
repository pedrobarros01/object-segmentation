import os
import tensorflow as tf
import numpy as np
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import matplotlib.pyplot as plt
# Carregar o modelo salvo
model = tf.keras.models.load_model('unet_model.h5')
# Caminhos para imagens e máscaras
IMAGE_DIR = 'database/VOC2012_train_val/VOC2012_train_val/JPEGImages/'
MASK_DIR = 'database/VOC2012_train_val/VOC2012_train_val/SegmentationClass/'

IMG_SIZE = (128, 128)  # Redimensionamento das imagens
NUM_CLASSES = 21  # Pascal VOC tem 21 classes (20 + 1 fundo)
def predict_image(image_path):
    """Carrega uma imagem e faz uma previsão da máscara."""
    # Carregar e pré-processar a imagem
    img = load_img(image_path, target_size=IMG_SIZE)
    img_array = img_to_array(img) / 255.0  # Normalizar entre [0, 1]
    img_array = np.expand_dims(img_array, axis=0)  # Adicionar batch dimension

    # Fazer a previsão
    prediction = model.predict(img_array)[0]  # Pega o primeiro item da previsão

    # Converter a previsão para rótulos de classe (classificação pixel a pixel)
    predicted_mask = np.argmax(prediction, axis=-1)  # Pegar a classe com maior valor
    predicted_mask = predicted_mask.astype(np.uint8)

    return predicted_mask

def visualize_prediction(image_path, predicted_mask):
    """Visualiza a imagem original e a máscara prevista lado a lado."""
    img = load_img(image_path, target_size=IMG_SIZE)
    plt.figure(figsize=(10, 5))

    # Imagem original
    plt.subplot(1, 2, 1)
    plt.imshow(img)
    plt.axis('off')
    plt.title("Imagem Original")

    # Máscara prevista
    plt.subplot(1, 2, 2)
    plt.imshow(predicted_mask, cmap='jet')  # Usar colormap para visualização
    plt.axis('off')
    plt.title("Máscara Prevista")

    plt.show()

# Exemplo de uso
image_path = os.path.join(IMAGE_DIR, '2007_000032.jpg')  # Substituir pelo nome da imagem desejada
predicted_mask = predict_image(image_path)
visualize_prediction(image_path, predicted_mask)
