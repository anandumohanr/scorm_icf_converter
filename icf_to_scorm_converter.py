import streamlit as st
import os
from io import BytesIO
from zipfile import ZipFile
import uuid
import shutil
import zipfile

# Conversion logic (simplified inline for Streamlit)
def convert_icf_to_scorm(uploaded_zip):
    working_dir = f"temp_{uuid.uuid4().hex[:8]}"
    extract_dir = os.path.join(working_dir, "extracted")
    scorm_dir = os.path.join(working_dir, "scorm_package")
    os.makedirs(extract_dir, exist_ok=True)
    os.makedirs(scorm_dir, exist_ok=True)

    # Save uploaded file temporarily
    temp_zip_path = os.path.join(working_dir, "input.zip")
    with open(temp_zip_path, "wb") as f:
        f.write(uploaded_zip.getbuffer())

    with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

    # Find nested folder (if any)
    nested_items = os.listdir(extract_dir)
    if len(nested_items) == 1 and os.path.isdir(os.path.join(extract_dir, nested_items[0])):
        nested_folder = os.path.join(extract_dir, nested_items[0])
    else:
        nested_folder = extract_dir

    shutil.copytree(nested_folder, scorm_dir, dirs_exist_ok=True)

    # Find main content HTML
    main_html = None
    for root, _, files in os.walk(scorm_dir):
        for f in files:
            if f.startswith("chapter") and f.endswith(".html"):
                main_html = os.path.relpath(os.path.join(root, f), scorm_dir)
                break
        if main_html:
            break

    if not main_html:
        raise Exception("Main HTML file not found")

    # Create index.html
    with open(os.path.join(scorm_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html lang='en'>
<head>
  <meta charset='UTF-8'>
  <title>ICF Unified SCORM</title>
  <style>
    iframe {{ width: 100%; height: 600px; border: 1px solid #ccc; margin-top: 10px; }}
    pre {{ background: #f4f4f4; padding: 10px; overflow: auto; }}
    section {{ margin-bottom: 30px; }}
  </style>
</head>
<body>
  <h1>Interactive Course</h1>
  <section><h2>Pre-Test</h2><div id='pretest'></div></section>
  <section><h2>Main Content</h2><iframe src='{main_html}'></iframe></section>
  <section><h2>Post-Test</h2><div id='posttest'></div></section>
  <script>
    function loadTest(id, jsonFile) {{
      fetch(jsonFile)
        .then(res => res.json())
        .then(data => {{
          document.getElementById(id).innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
        }});
    }}
    loadTest("pretest", "test/pretest.json");
    loadTest("posttest", "test/posttest.json");
  </script>
</body>
</html>
""")

    # Create imsmanifest.xml
    with open(os.path.join(scorm_dir, "imsmanifest.xml"), "w", encoding="utf-8") as f:
        f.write(f"""<?xml version='1.0' encoding='UTF-8'?>
<manifest identifier='ICFtoSCORM' version='1.0'
  xmlns='http://www.imsproject.org/xsd/imscp_rootv1p1p2'
  xmlns:adlcp='http://www.adlnet.org/xsd/adlcp_rootv1p2'
  xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'
  xsi:schemaLocation='http://www.imsproject.org/xsd/imscp_rootv1p1p2
  imscp_rootv1p1p2.xsd
  http://www.adlnet.org/xsd/adlcp_rootv1p2
  adlcp_rootv1p2.xsd'>
  <metadata><schema>ADL SCORM</schema><schemaversion>1.2</schemaversion></metadata>
  <organizations default='ORG1'>
    <organization identifier='ORG1'>
      <title>Unified ICF Course</title>
      <item identifier='ITEM1' identifierref='RES1'>
        <title>ICF Full Course</title>
      </item>
    </organization>
  </organizations>
  <resources>
    <resource identifier='RES1' type='webcontent' adlcp:scormtype='sco' href='index.html'>
      <file href='index.html'/>
    </resource>
  </resources>
</manifest>
""")

    # Create output ZIP
    output_zip = BytesIO()
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for foldername, _, filenames in os.walk(scorm_dir):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                arcname = os.path.relpath(file_path, scorm_dir)
                zipf.write(file_path, arcname)

    output_zip.seek(0)
    shutil.rmtree(working_dir)
    return output_zip

# Streamlit UI
st.title("ICF to SCORM Converter")
st.write("Upload your `.icf` or `.zip` file to convert it to a SCORM 1.2 package.")

uploaded_file = st.file_uploader("Upload ICF file", type=["zip", "icf"])

if uploaded_file:
    try:
        scorm_package = convert_icf_to_scorm(uploaded_file)
        st.success("SCORM package created successfully!")
        st.download_button("Download SCORM Package", scorm_package, file_name="scorm_package.zip")
    except Exception as e:
        st.error(f"Conversion failed: {str(e)}")
