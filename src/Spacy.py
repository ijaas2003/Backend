import spacy;

nlp = spacy.load('en_core_web_sm');

Text = "Tamil Nadu,located in the southern part of India, has a diverse economy with a mix of agriculture, manufacturing,and services sectors. In the early 2000s, the state experienced significant growth, driven by industries such as textiles, automobiles, elect ronics, and software services. Chennai, the capital city, emerged as a major hub for IT and IT -enabled services, attracting investments from both domestic and international firms.The agricultural sector remains important, with rice, sugarcane, and cotton being the primary crops. Tamil Nadu is also a leader in horticulture, producing fruits and vegetables for domestic consumption and export.The state government has been proactive in promoting industrial development through various incentives and policies, leading to the establishment of industrial estates and special economic zones.However, Tamil Nadu faces challenges such as water scarcity, infrastructure bottlenecks, and skill shortages.Despite these challenges, the state's economy continued to grow steadily during the 2000s, contributing significantly to India's overall economic growth. Overall, Tamil Nadu's economy in the early 2000s was characterized by a vibrant industrial sector, supported by a robust services industry and a resilient agricultural base."
doc = nlp(Text);
print(len(doc), len(Text))

Sent = list(doc.sents)[0];
print(Sent[4].left);


    