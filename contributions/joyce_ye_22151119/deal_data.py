
import re

html = """
<p><span style="font-size:11.0pt"><span style="font-family:&quot;Arial&quot;,sans-serif">WorkCover WA requires the provision of application development services procured under CUAICTS2015.</span></span></p>
<p style="margin-left:0cm; margin-right:0cm"><span style="font-size:11.0pt"><span style="font-family:&quot;Arial&quot;,sans-serif">The deliverables&nbsp;are:</span></span></p>
<ul style="list-style-type:square">
<li><span style="font-size:11.0pt"><span style="font-family:&quot;Arial&quot;,sans-serif">development of the Arbitration and Settlements Online Services; and</span></span></li>
<li><span style="font-size:11.0pt"><span style="font-family:&quot;Arial&quot;,sans-serif">successful deployment of the Arbitration and Settlements Online Services.</span></span></li>
</ul>
"""

text = re.findall(r'>([^<]+)<', html)
import re

html = """
<p><span style="font-size:11.0pt"><span style="font-family:&quot;Arial&quot;,sans-serif">WorkCover WA requires the provision of application development services procured under CUAICTS2015.</span></span></p>
<p style="margin-left:0cm; margin-right:0cm"><span style="font-size:11.0pt"><span style="font-family:&quot;Arial&quot;,sans-serif">The deliverables&nbsp;are:</span></span></p>
<ul style="list-style-type:square">
<li><span style="font-size:11.0pt"><span style="font-family:&quot;Arial&quot;,sans-serif">development of the Arbitration and Settlements Online Services; and</span></span></li>
<li><span style="font-size:11.0pt"><span style="font-family:&quot;Arial&quot;,sans-serif">successful deployment of the Arbitration and Settlements Online Services.</span></span></li>
</ul>
"""

text = re.findall(r'>([^<]+)<', html)
text = [t.strip() for t in text if t.strip()]
print(text)
print(text)
