import io
import zipfile

def zipfile_to_bytesio(zip_file):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_output:
        for zip_info in zip_file.infolist():
            file_content = zip_file.read(zip_info.filename)
            zip_output.writestr(zip_info, file_content)
    zip_buffer.seek(0)
    return zip_buffer

if __name__ == "__main__":
    pass
