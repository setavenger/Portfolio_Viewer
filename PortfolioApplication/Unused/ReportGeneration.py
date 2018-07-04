
import plotly.plotly as py
from IPython.display import display, HTML
from xhtml2pdf import pisa
import base64

width = 600
height = 600

template = (''
    '<img style="width: {width}; height: {height}" src="data:image/png;base64,{image}">' 
    '{caption}'                              # Optional caption to include below the graph
    '<br>'
    '<hr>'
'')

# A collection of Plotly graphs
figures = [
    {'data': [{'x': [1,2,3], 'y': [3,1,6]}], 'layout': {'title': 'the first graph'}},
    {'data': [{'x': [1,2,3], 'y': [3,7,6], 'type': 'bar'}], 'layout': {'title': 'the second graph'}}
]

# Generate their images using `py.image.get`
images = [base64.b64encode(py.image.get(figure, width=width, height=height)).decode('utf-8') for figure in figures]

report_html = ''
for image in images:
    _ = template
    _ = _.format(image=image, caption='', width=width, height=height)
    report_html += _


# Utility function
def convert_html_to_pdf(source_html, output_filename):
    # open output file for writing (truncated binary)
    result_file = open(output_filename, "w+b")

    # convert HTML to PDF
    pisa_status = pisa.CreatePDF(
            source_html,                # the HTML to convert
            dest=result_file)           # file handle to recieve result

    # close output file
    result_file.close()                 # close output file

    # return True on success and False on errors
    return pisa_status.err


display(HTML(report_html))
convert_html_to_pdf(report_html, 'report-2.pdf')
