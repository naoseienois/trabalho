
import zipfile, os

proj = '/home/user/restaurante'
zip_path = '/home/user/restaurante_cuscuz.zip'

arquivos = sorted(os.listdir(proj))

with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for arq in arquivos:
        zf.write(f'{proj}/{arq}', arq)

print(f"ZIP criado: {os.path.getsize(zip_path)/1024:.1f} KB")
print("Conteúdo:")
with zipfile.ZipFile(zip_path, 'r') as zf:
    for nome in zf.namelist():
        print(f"  {nome}")
