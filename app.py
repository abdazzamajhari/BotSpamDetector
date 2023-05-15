from flask import Flask, Response, request, render_template
import io
import csv
from io import StringIO

import pandas as pd
import re

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# fungsi untuk mengimpor fungsi enumerate() ke dalam template
@app.context_processor
def inject_enumerate():
    return dict(enumerate=enumerate)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/res', methods=['POST'])
def result():
    global tweets_df  # Declare tweets_df as global to modify it within the function
    if request.method == 'POST':
        f = request.files['data_file']
        if not f:
            return "No file"

        stream = io.StringIO(f.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.reader(stream)
        print(csv_input)
        for row in csv_input:
            print(row)

        stream.seek(0)
        result = stream.read()
        # load data
        tweets_df = pd.read_csv(StringIO(result), sep="|")

        # Konversi tipe data kolom tertentu
        tweets_df["tanggal"] = pd.to_datetime(tweets_df["tanggal"])
        
        # Menghapus semua baris yang memiliki nilai NaN
        tweets_df = tweets_df.dropna()

        def cleanTxt(text):
            # Menghapus mention dan username dengan ekspresi reguler
            text = re.sub(r'@\w+(_\w+)* ?', '', text)
            # Menghapus '#' hash tag
            text = re.sub(r'#', '', text) 
            # Menghapus '_' underscore
            text = re.sub(r'_', '', text)
            # Menghapus ':' 
            text = re.sub(r':', '', text)
            # Menghapus retweet (RT)
            text = re.sub(r'RT[\s]+', '', text)
            # Menghapus hyperlink (URL)
            text = re.sub(r'https?\/\/\S+', '', text)
            # Menghapus ' --> quotes
            text = re.sub(r"'", '', text) 
            # Menghapus enter
            text = re.sub(r'\n', ' ', text)
            # Menghapus emotikon
            emoji_pattern = re.compile("["
                u"\U0001F600-\U0001F64F"  # emotikon wajah
                u"\U0001F300-\U0001F5FF"  # emotikon simbol dan benda
                u"\U0001F680-\U0001F6FF"  # emotikon transportasi dan teknologi
                u"\U0001F1E0-\U0001F1FF"  # emotikon bendera negara
                u"\U00002702-\U000027B0"  # emotikon tanda dan simbol
                u"\U000024C2-\U0001F251" 
                "]+", flags=re.UNICODE)
            text = emoji_pattern.sub(r'', text)
            # Menghapus double empty space
            text = re.sub(r'\s+', ' ', text)
            return text

        tweets_df['tweet'] = tweets_df['tweet'].apply(cleanTxt)
        tweets_df['tweet'] = tweets_df['tweet'].str.lower()

        # Menggunakan CountVectorizer untuk mengubah kata menjadi vektor
        vectorizer = CountVectorizer().fit_transform(tweets_df['tweet'])

        # Menghitung similarity antara semua pasangan dokumen
        similarity_matrix = cosine_similarity(vectorizer)

        # Menentukan threshold similarity untuk mengklasifikasikan tweet sebagai bot/spam
        threshold = 0.8

        # Membuat set untuk menyimpan tweet yang sudah pernah muncul
        seen_tweets = set()

        # Membuat dictionary untuk menyimpan jumlah tweet yang sudah diposting oleh masing-masing user
        user_tweet_count = {}

        # Membuat list untuk menyimpan hasil klasifikasi
        classification = []

        # Loop untuk setiap tweet
        for i in range(len(tweets_df)):
            tweet_text = tweets_df['tweet'][i]
            username = tweets_df['username'][i]
            tweet_date = tweets_df['tanggal'][i].date()

            # Cek apakah tweet sudah pernah muncul sebelumnya atau apakah user sudah posting terlalu banyak tweet dengan karakteristik yang sama pada tanggal yang sama
            if tweet_text in seen_tweets or (username in user_tweet_count and user_tweet_count[username]['date'] == tweet_date and user_tweet_count[username]['count'] > 5):
                classification.append(("Bot/Spam", 0))
            else:
                # Tambahkan tweet ke set seen_tweets
                seen_tweets.add(tweet_text)

                # Tambahkan jumlah tweet yang sudah diposting oleh user pada tanggal yang sama
                if username in user_tweet_count and user_tweet_count[username]['date'] == tweet_date:
                    user_tweet_count[username]['count'] += 1
                else:
                    user_tweet_count[username] = {'date': tweet_date, 'count': 1}

                # Mencari index tweet dengan similarity tertinggi
                max_similarity_index = similarity_matrix[i].argsort()[-2]
                # Mencari nilai similarity tertinggi
                max_similarity = similarity_matrix[i][max_similarity_index]
                # Jika nilai similarity tertinggi melebihi threshold, maka tweet dianggap sebagai bot/spam
                if max_similarity > threshold:
                    classification.append(("Bot/Spam", max_similarity))
                else:
                    classification.append(("Manusia", max_similarity))

        # Menambahkan kolom baru untuk menyimpan hasil klasifikasi dan skor similarity
        klasifikasi, skor_similarity = zip(*classification)
        tweets_df['klasifikasi'] = klasifikasi
        # tweets_df['skor_similarity'] = skor_similarity

        # Melihat data yang ditweet manusia
        manusia_df = tweets_df[tweets_df['klasifikasi'] == 'Manusia']

    return render_template('index.html', tweets=manusia_df.values.tolist())


@app.route('/download')
def download_csv():
    global tweets_df  # Declare tweets_df as global to access it within the function
    if tweets_df is None:
        return "No data to download"
    output = io.StringIO()
    writer = csv.writer(output, delimiter='|')
    writer.writerow(['tweet', 'username', 'tanggal_tweet', 'klasifikasi'])
    for row in tweets_df.itertuples(index=False):
        writer.writerow(row)
    output.seek(0)
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=result.csv"}
    )

if __name__ == "__main__": 
    app.run(host="0.0.0.0", port=3300)