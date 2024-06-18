import os

def collect_files(max_lines_per_file=1000):
    project_path = os.path.dirname(os.path.abspath(__file__))  # Определяем путь к корневой директории проекта
    output_dir = os.path.join(project_path, 'collected_files')
    os.makedirs(output_dir, exist_ok=True)  # Создаем директорию для выходных файлов, если она не существует

    file_counter = 1
    line_counter = 0
    output_file = os.path.join(output_dir, f'project_files_part_{file_counter}.txt')
    out_file = open(output_file, 'w', encoding='utf-8')
    print(f"Creating file: {output_file}")

    for root, dirs, files in os.walk(project_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        code = f.readlines()
                    except UnicodeDecodeError as e:
                        print(f"Error reading {file_path}: {e}")
                        continue
                
                if line_counter + len(code) > max_lines_per_file:
                    out_file.close()
                    file_counter += 1
                    output_file = os.path.join(output_dir, f'project_files_part_{file_counter}.txt')
                    out_file = open(output_file, 'w', encoding='utf-8')
                    print(f"Creating file: {output_file}")
                    line_counter = 0
                
                out_file.write(f"# File: {file_path}\n")  # Записываем название файла
                out_file.writelines(code)
                out_file.write("\n\n# End of file\n\n")
                line_counter += len(code) + 3

    out_file.close()

if __name__ == "__main__":
    collect_files()
    print("All files collected and split into parts in the 'collected_files' directory.")
