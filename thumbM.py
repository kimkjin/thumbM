import os
import cv2
import random
import numpy as np
import pickle
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import collections


LEGEND_COLOR_CODES = ['#ffffff', '#000002', '#000000']
NUM_RANDOM_FRAMES = 6000


def capture_random_frame(video_path, output_dir):
    video_capture = cv2.VideoCapture(video_path)
    total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_rate = video_capture.get(cv2.CAP_PROP_FPS)

    # Calcula o número total de frames a serem ignorados no início e no final do vídeo
    frames_to_skip_start = int(frame_rate * 60 * 4)  # 5 minutos
    frames_to_skip_end = int(frame_rate * 60 * 3)  # 3 minutos

    # Obtendo o nome do arquivo de vídeo sem a extensão
    video_name = os.path.splitext(os.path.basename(video_path))[0]

    # Calcula o intervalo de frames válidos
    valid_frame_range_start = frames_to_skip_start
    valid_frame_range_end = total_frames - frames_to_skip_end

    if valid_frame_range_end <= valid_frame_range_start:
        log_text.insert(END, f"Vídeo muito curto: {video_name}\n")
        log_text.tag_add("error", f"{float(log_text.index(END)) - len(video_name) - 1} linestart", f"{float(log_text.index(END)) - 1} lineend")
        log_text.tag_config("error", foreground="red")
        video_capture.release()
        return

    frame_without_subtitles = None

    while frame_without_subtitles is None:
        # Escolhe um frame aleatório dentro do intervalo válido
        frame_number = random.randint(valid_frame_range_start, valid_frame_range_end)

        # Avança para o frame escolhido
        video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

        # Captura o frame
        success, frame = video_capture.read()
        if success:
            # Verifica se o frame contém legendas
            subtitles = detect_subtitles(frame)

            # Verifica se o frame possui no mínimo 256 cores
            colors = extract_frame_colors(frame)
            color_counts = collections.Counter(tuple(color) for color in colors)
            num_unique_palettes = len(color_counts.keys())
            if not subtitles and num_unique_palettes >= 512:
                frame_without_subtitles = frame

    # Define o caminho de saída do arquivo de captura de tela com o mesmo nome do vídeo
    output_file = os.path.join(output_dir, f'{video_name}.webp')
    cv2.imwrite(output_file, frame_without_subtitles, [cv2.IMWRITE_WEBP_QUALITY, 100])
    log_text.insert(END, f"Capturada a tela do vídeo: {video_name}\n")

    video_capture.release()


def extract_frame_colors(frame):
    # Converte o frame para o espaço de cores RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Redimensiona o frame para reduzir o tempo de processamento
    resized_frame = cv2.resize(rgb_frame, (100, 100))

    # Converte o frame para uma lista de cores RGB
    colors = resized_frame.reshape(-1, 3).tolist()

    return colors


def detect_subtitles(frame):
    # Convertendo o frame para o espaço de cores HSV
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Convertendo os códigos de cores das legendas para o espaço de cores HSV
    legend_color_hsv = [color_code_to_hsv(code) for code in LEGEND_COLOR_CODES]

    # Verificando se as cores das legendas estão presentes no frame
    for color_hsv in legend_color_hsv:
        mask = cv2.inRange(hsv_frame, color_hsv - np.array([10, 50, 50]), color_hsv + np.array([10, 50, 50]))
        if np.any(mask):
            return True

    return False

def color_code_to_hsv(color_code):
    rgb = tuple(int(color_code[i:i+2], 16) for i in (1, 3, 5))
    hsv = cv2.cvtColor(np.uint8([[rgb]]), cv2.COLOR_RGB2HSV)
    return hsv[0][0]


def select_video_directory():
    video_dir = filedialog.askdirectory()
    video_dir_entry.delete(0, END)
    video_dir_entry.insert(END, video_dir)

def select_output_directory():
    output_dir = filedialog.askdirectory()
    output_dir_entry.delete(0, END)
    output_dir_entry.insert(END, output_dir)

def process_videos():
    video_dir = video_dir_entry.get()
    output_dir = output_dir_entry.get()

    if not os.path.isdir(video_dir):
        messagebox.showerror("Erro", "Selecione um diretório de vídeos válido.")
        return

    if not os.path.isdir(output_dir):
        messagebox.showerror("Erro", "Selecione um diretório de saída válido.")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    processed_videos = []
    total_videos = len([filename for filename in os.listdir(video_dir) if os.path.isfile(os.path.join(video_dir, filename))])

    log_text.delete(1.0, END)

    progress_var.set(0)
    progress_bar['maximum'] = 100

    for i, filename in enumerate(os.listdir(video_dir)):
        file_path = os.path.join(video_dir, filename)

        if os.path.isfile(file_path):
            video_ext = os.path.splitext(filename)[1].lower()
            if video_ext in ['.mp4', '.mkv', '.avi', '.webm']:
                capture_random_frame(file_path, output_dir)
                processed_videos.append(filename)
            else:
                log_text.insert(END, f"Vídeo não processado devido a extensão inválida: {filename}\n")
                log_text.tag_add("error", f"{log_text.index(END) - len(filename) - 1} linestart", f"{log_text.index(END) - 1} lineend")
                log_text.tag_config("error", foreground="red")

        progress = (i + 1) / total_videos * 100
        progress_var.set(progress)
        root.update()

    if len(processed_videos) == 0:
        messagebox.showwarning("Aviso", "Nenhum vídeo foi capturado.")
    elif len(processed_videos) == len(os.listdir(video_dir)):
        log_text.insert(END, "Todos os vídeos foram capturados com sucesso.\n")
        messagebox.showinfo("Sucesso", "Todos os vídeos foram capturados com sucesso.")
    else:
        missing_videos = [filename for filename in os.listdir(video_dir) if filename not in processed_videos]
        log_text.insert(END, "Alguns vídeos não foram capturados:\n")
        for video in missing_videos:
            log_text.insert(END, f"- {video}\n")
            log_text.tag_add("error", f"{log_text.index(END) - len(video) - 1} linestart", f"{log_text.index(END) - 1} lineend")
            log_text.tag_config("error", foreground="red")
        messagebox.showwarning("Aviso", f"Alguns vídeos não foram capturados. Consulte a área de log para mais detalhes.")

    save_output_directory(output_dir)

def save_output_directory(output_dir):
    with open("output_dir.pickle", "wb") as file:
        pickle.dump(output_dir, file)

def load_output_directory():
    if os.path.exists("output_dir.pickle"):
        with open("output_dir.pickle", "rb") as file:
            output_dir = pickle.load(file)
            output_dir_entry.insert(END, output_dir)

root = Tk()
root.title("ThumbM™  by  Kim")
# Obtendo a largura e altura da tela
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Definindo o tamanho da janela
window_width = 600
window_height = 400

# Calculando a posição x e y para centralizar a janela
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2

# Definindo a posição da janela
root.geometry(f"{window_width}x{window_height}+{x}+{y}")
root.configure(bg="#36393f")
root.resizable(False, False)

# Definindo estilos
style = ttk.Style()
style.theme_use("clam")
style.configure(".", background="#36393f", foreground="#ffffff", font=("Arial", 10))

# Definindo estilos personalizados
style.configure("TButton", padding=3, background="#7289da", foreground="#ffffff")
style.map("TButton", background=[("active", "#7289da")])
style.configure("Horizontal.TProgressbar", thickness=6, troughcolor="#2f3136", background="#7289da")

# Frame principal
main_frame = ttk.Frame(root)
main_frame.pack(pady=20)

# Campo de seleção do diretório dos vídeos
video_dir_frame = ttk.Frame(main_frame)
video_dir_frame.pack()

video_dir_label = ttk.Label(video_dir_frame, text="Diretório dos Vídeos:")
video_dir_label.pack(side=LEFT, padx=(0, 5))

video_dir_entry = ttk.Entry(video_dir_frame, width=40)
video_dir_entry.pack(side=LEFT, padx=(0, 5))

video_dir_button = ttk.Button(video_dir_frame, text="Selecionar", command=select_video_directory)
video_dir_button.pack(side=LEFT, padx=(0, 5))

# Estilo personalizado para o campo de seleção do diretório dos vídeos
style.configure("Custom.TEntry", fieldbackground="#383a40")
video_dir_entry.configure(style="Custom.TEntry")

# Campo de seleção do diretório de saída
output_dir_frame = ttk.Frame(main_frame)
output_dir_frame.pack()

output_dir_label = ttk.Label(output_dir_frame, text="Diretório de Saída:")
output_dir_label.pack(side=LEFT, padx=(0, 5))

output_dir_entry = ttk.Entry(output_dir_frame, width=40)
output_dir_entry.pack(side=LEFT, padx=(0, 5))

output_dir_button = ttk.Button(output_dir_frame, text="Selecionar", command=select_output_directory)
output_dir_button.pack(side=LEFT, padx=(0, 5))

# Estilo personalizado para o campo de seleção do diretório de saída
output_dir_entry.configure(style="Custom.TEntry")

# Carregar o diretório de saída anteriormente selecionado
load_output_directory()

# Botão de processamento
process_button = ttk.Button(root, text="Processar Vídeos", command=process_videos)
process_button.pack(pady=20)

# Barra de progresso
progress_var = DoubleVar()
progress_bar = ttk.Progressbar(root, style="Horizontal.TProgressbar", length=400, mode="determinate", variable=progress_var)
progress_bar.pack(pady=10)

# Área de log
log_frame = ttk.Frame(root)
log_frame.pack()

log_label = ttk.Label(log_frame, text="Registro de Processamento:")
log_label.pack()

log_text = Text(log_frame, width=60, height=10)
log_text.pack()

root.mainloop()