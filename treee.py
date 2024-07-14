import os

def list_files(startpath):
    ignore_dirs = {'.git', '__pycache__', '00'}  # Добавьте сюда другие папки, которые вы хотите игнорировать
    tree_str = ""
    for root, dirs, files in os.walk(startpath, topdown=True):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]  # Игнорируем не нужные директории
        level = root.replace(startpath, '').count(os.sep)
        indent = '│   ' * (level - 1) + '├── ' if level > 0 else ''
        tree_str += f"{indent}{os.path.basename(root)}/\n"
        subindent = '│   ' * level + '└── '
        for i, file in enumerate(files):
            if file.endswith('.py') or file.endswith('.html'):  # Учитываем только .py и .html файлы
                if i == len(files) - 1:  # Последний файл в папке
                    subindent = '│   ' * level + '    '
                tree_str += f"{subindent}{file}\n"
    return tree_str

# Укажите путь к корневой директории вашего проекта
project_root = r"C:\Users\p4ul7\OneDrive\מסמכים\Mimino"

# Генерируем древовидное представление
project_tree = list_files(project_root)

# Укажите путь и имя файла, куда вы хотите сохранить древовидную структуру
output_file = r"C:\Users\p4ul7\OneDrive\מסמכים\Mimino\project_structure.txt"

# Записываем древовидную структуру в файл
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(project_tree)

print(f"Древовидная структура проекта сохранена в файл: {output_file}")
