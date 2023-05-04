from peer_config import *
import datetime, block, re
from xhtml2pdf import pisa
from jinja2 import Environment, FileSystemLoader
from pypdf import PdfReader
from pyhanko.sign import signers
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from oscrypto import keys
from pyhanko_certvalidator import ValidationContext
from pyhanko_certvalidator.errors import InvalidCertificateError
from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.sign.validation import validate_pdf_signature, settings
from cryptography import x509
from typing import Tuple


fields: Tuple = ("institution","name","registeredNumber","stream","degree","issuedDate","hash")

cert_file = open("keys/cert.pem", 'r').readlines()
cert_data = "".join(cert_file)
root_cert = keys.parse_certificate(cert_data.encode())
vc = ValidationContext(trust_roots=[root_cert],allow_fetching=True)
key_usage = set(['non_repudiation','digital_signature'])

environment = Environment(loader=FileSystemLoader("templates/"))
template = environment.get_template("certificate.html")

pdf_text_template = '(.*)\n \n Certificate of Completion\n \n This certificate is presented to\n \n (.*)\n with (.*) for passing\n \n (.*)\n \n(.*)\n awarded on (.*)\n (.*)\n '

def generate_block(dict_block):
    block_object = block.Block(
    index = int(dict_block["index"]),
    timestamp = dict_block["timestamp"],
    previous_hash = dict_block["previous_hash"],
    hash = dict_block["hash"],
    data = dict_block["data"],
    reference_blocks=dict_block["reference_blocks"],
    nonce = int(dict_block["nonce"])
    )
    return block_object


def create_new_block_from_previous(previous_block=None, data=None, reference_blocks=None, timestamp=None, nonce=None, hash=None):
    if not previous_block:
        index = 0
        previous_hash = ''
    else:
        index = int(previous_block.index) + 1
        previous_hash = previous_block.hash
    if not data:
        return None
    new_block = block.Block(index=index, data=data, previous_hash=previous_hash, reference_blocks=reference_blocks,timestamp=timestamp, nonce=nonce, hash=hash)
    return new_block

def validate_string(s):
    words = s.split()
    for word in words:
        if not word.isalpha():
            return False
    return True

def validate_data(data):
    for k,v in data.items():
        if k=="issuedDate":
            date_format = "%d/%m/%Y"
            if datetime.datetime.strptime(v, date_format) is False:
                return False
        elif k =="registeredNumber":
            if v.isalnum() is False:
                return False
        else:
            if (0 < len(v) < 100 and validate_string(v)) is False:
                return False
    return True

def format_data(request_data):
    data = dict(request_data)
    formatted_data = {}
    if validate_data(data):
        for k,v in data.items():
            if k=="issuedDate" or k=="registeredNumber":
                formatted_data[k] = v
            else:
                formatted_data[k] = str(v).upper()
        return formatted_data
    else:
        return None

def sign_pdf(pdf_file):
    cms_signer = signers.SimpleSigner.load(key_file='keys/key.pem',cert_file='keys/cert.pem')
    pdf_name_path = pdf_file.split(".")
    signed_pdf_file = pdf_name_path[0]+"-signed."+pdf_name_path[1]
    with open(pdf_file, 'rb') as doc:
        w = IncrementalPdfFileWriter(doc)
        out = signers.PdfSigner(
            signers.PdfSignatureMetadata(field_name='BlockSignature',signer_key_usage=key_usage),
            signer=cms_signer,
        ).sign_pdf(w)
        with open(signed_pdf_file, 'wb') as f:
            f.write(out.getbuffer())
            f.close()
        doc.close()

def format_cert_data(sig_cert_data):
    issuer_data = dict()
    for kv in str(sig_cert_data.issuer.human_friendly).split(","):
        temp =kv.split(":")
        issuer_data[temp[0]] = temp[1]
    sig_cert_data_fmt = {
        'issuer': issuer_data,
        'sha1': sig_cert_data.sha1.hex(),
        'publicKey': sig_cert_data.public_key.sha256.hex()
    }
    return sig_cert_data_fmt

def validate_pdf(temp_pdf_file):
    try:
        doc = temp_pdf_file.file._file
        r = PdfFileReader(doc)
        sig = r.embedded_signatures[0]
        status = validate_pdf_signature(sig, vc, key_usage_settings=settings.KeyUsageConstraints(key_usage=key_usage))
        sig_cert_data: x509.Certificate = status.signing_cert
        sig_pdf_data_fmt = format_cert_data(sig_cert_data)
        sig_pdf_data_fmt.update({'signingTime':status.signer_reported_dt.isoformat() ,'sigIntact':status.intact,'sigCoverage': str(status.coverage), 'sigValid': status.valid, 'summary': status.summary()})
        sig_pdf_data_fmt["data"] = get_pdf_data(doc)
        return sig_pdf_data_fmt
    except InvalidCertificateError:
        pass
    except Exception as e:
        print(e)
        return False

def get_pdf_data(pdf_file):
    try:
        doc = PdfReader(pdf_file)
        page_text = doc.pages[0].extract_text()
        text_data = re.findall(pdf_text_template,page_text)
        return dict(zip(fields,text_data[0]))
    except Exception as e:
        print(e)
        return None

def check_data(pdf_data,block_data):
    temp_pdf_data, temp_block_data = pdf_data.copy(), block_data.copy()
    del temp_block_data["parentName"]
    del temp_pdf_data["hash"]
    return temp_pdf_data==temp_block_data

def generate_pdf_with_data(block):
    try:
        certificate_name = CERTIFICATES+str(block.get_index())+".pdf"
        certificate_file = open(certificate_name, "w+b")
        html_string = template.render(data=block.get_data(), hash=block.get_hash())
        pdfGenerationStatus = pisa.CreatePDF(html_string,certificate_file)
        certificate_file.close()
        sign_pdf(certificate_name)
        return pdfGenerationStatus.err
    except Exception as e:
        print(e)
        return False
    

    