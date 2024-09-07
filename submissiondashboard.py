import numpy as np
import seaborn as sns
import pandas as pd
import pickle
import matplotlib.pyplot as plt
import zipfile
import streamlit as st
import unidecode
import datetime as dt
from streamlit_option_menu import option_menu



all_df = pd.read_csv('all_data.csv')

with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    selected = option_menu("Main Menu", ["Order Bulanan", "Performa Produk", 'Status Pesanan','Waktu Pengiriman', 'RFM Analisis'], 
        icons=['calendar', "bar-chart", 'clipboard-check','clock','grid'], menu_icon="cast", default_index=0)
    selected
    
if 'order_approved_at' in all_df.columns:
    all_df['order_approved_at'] = pd.to_datetime(all_df['order_approved_at'], errors='coerce')
else:
    print("Kolom 'order_approved_at' tidak ditemukan!")

# change type str/obj -> datetime
datetime_columns = ["order_approved_at"]
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df['order_approved_at'])


def number_order_per_month(df):
    monthly_df = df.resample(rule='M', on='order_approved_at').agg({
        "order_id": "size",
    })
    monthly_df.index = monthly_df.index.strftime('%B') #mengubah format order_approved_at menjadi Tahun-Bulan
    monthly_df = monthly_df.reset_index()
    monthly_df.rename(columns={
        "order_id": "order_count",
    }, inplace=True)
    monthly_df = monthly_df.sort_values('order_count').drop_duplicates('order_approved_at', keep='last')
    month_mapping = {
        "January": 1,"February": 2,"March": 3,"April": 4,"May": 5,"June": 6,"July": 7,"August": 8,"September": 9,"October": 10,"November": 11,"December": 12}

    monthly_df["month_numeric"] = monthly_df["order_approved_at"].map(month_mapping)
    monthly_df = monthly_df.sort_values("month_numeric")
    monthly_df = monthly_df.drop("month_numeric", axis=1)
    return monthly_df 

def create_by_product_df(df):
    product_id_counts = df.groupby('product_category_name_english')['product_id'].count().reset_index()
    sorted_df = product_id_counts.sort_values(by='product_id', ascending=False)
    return sorted_df

def create_rfm(df):
    now=dt.datetime(2018,10,30)

    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    # Group by 'customer_id' and calculate Recency, Frequency, and Monetary
    recency = (now - df.groupby('customer_id')['order_purchase_timestamp'].max()).dt.days
    frequency = df.groupby('customer_id')['order_id'].count()
    monetary = df.groupby('customer_id')['price'].sum()

    # Create a new DataFrame with the calculated metrics
    rfm = pd.DataFrame({
        'customer_id': recency.index,
        'Recency': recency.values,
        'Frequency': frequency.values,
        'Monetary': monetary.values
    })
    
    col_list = ['customer_id','Recency','Frequency','Monetary']
    rfm.columns = col_list
    return rfm
 
# functions
daily_orders_df=number_order_per_month(all_df)
most_and_least_products_df=create_by_product_df(all_df)
rfm=create_rfm(all_df)

items_orders_df = pd.read_csv('all_data.csv')
avg_freight_by_status = items_orders_df.groupby('order_status')['freight_value'].mean().reset_index()

cust_orders_df= pd.read_csv('all_data.csv')
avg_delivery_time_diff_by_city = cust_orders_df.groupby('customer_city')['delivery_time_difference'].mean()
top_10_cities = avg_delivery_time_diff_by_city.sort_values(ascending=False).head(10)

freight_status_group = items_orders_df.groupby(['freight_value', 'order_status']).size().reset_index(name='count')
average_freight_per_order = items_orders_df['freight_value'].mean()

# Menghitung total jumlah pesanan
total_orders = items_orders_df.shape[0]

# Menghitung jumlah pesanan yang dibatalkan
canceled_orders = items_orders_df[items_orders_df['order_status'] == 'canceled'].shape[0]

# Menghitung tingkat pembatalan
cancellation_rate = (canceled_orders / total_orders) * 100

# ========================================================================================
# ======================================== Header ========================================
# ========================================================================================

st.header('Submission Analisis Data E-Commerce :sparkles:')

# SideBar
if selected == "Order Bulanan":
    # ========================================================================================
    # ================================= Order Bulanan ========================================
    # ========================================================================================
    st.header('Bagaimana Performa Penjualan e-Commerce dalam Beberapa Bulan Terakhir?')
    st.subheader('Order Bulanan')
    col1, col2 = st.columns(2)

    with col1:
        high_order_num = daily_orders_df['order_count'].max()
        high_order_month = daily_orders_df[daily_orders_df['order_count'] == daily_orders_df['order_count'].max()]['order_approved_at'].values[0]
        st.markdown(f"Highest orders in {high_order_month} : **{high_order_num}**")

    with col2:
        low_order = daily_orders_df['order_count'].min()
        low_order_month = daily_orders_df[daily_orders_df['order_count'] == daily_orders_df['order_count'].min()]['order_approved_at'].values[0]
        st.markdown(f"Lowest orders in {low_order_month} : **{low_order}**")

    fig, ax = plt.subplots(figsize=(16, 8))
    ax.plot(
        daily_orders_df["order_approved_at"],
        daily_orders_df["order_count"],
        marker='o',
        linewidth=2,
        color='red',
    )
    plt.xticks(rotation=45)
    ax.tick_params(axis='y', labelsize=20)
    ax.tick_params(axis='x', labelsize=15)

    st.pyplot(fig)

    st.subheader('Detail Order Bulanan')
    with st.expander('Lihat Detail Order Bulanan'):
        st.dataframe(daily_orders_df)

    with st.expander("Lihat Penjelasan"):
        st.write(
        """Dari data penjualan e-commerce yang tersedia, penjualan tertinggi terjadi pada bulan November dengan 9.017 pesanan, sementara penjualan terendah tercatat pada bulan September dengan 5.211 pesanan. Peningkatan signifikan di bulan November kemungkinan besar disebabkan oleh event belanja seperti Black Friday atau Cyber Monday, yang mendorong peningkatan aktivitas belanja. Sebaliknya, bulan September yang tidak memiliki event besar cenderung menunjukkan penurunan aktivitas belanja."""
        )
        st.write(
        """Tren ini menunjukkan bahwa penjualan e-commerce sangat dipengaruhi oleh faktor musiman dan event promosi. Perusahaan e-commerce dapat menggunakan data ini untuk mengoptimalkan strategi pemasaran dan manajemen inventaris, memastikan mereka siap menghadapi lonjakan permintaan dan mengurangi dampak dari bulan-bulan dengan penjualan lebih rendah."""
        )

elif selected == "Performa Produk":
    # ========================================================================================
    # ================================ Performa Produk =======================================
    # ========================================================================================
    st.header('Produk apa yang paling banyak terjual dan paling sedikit terjual?')
    st.subheader("Produk yang paling banyak dan paling sedikit terjual ")
    col1, col2 = st.columns(2)

    with col1:
        highest_product_sold = most_and_least_products_df['product_id'].max()
        st.markdown(f"Higest Number : **{highest_product_sold}**")

    with col2:
        lowest_product_sold = most_and_least_products_df['product_id'].min()
        st.markdown(f"Lowest Number : **{lowest_product_sold}**")

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(16, 8))

    colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

    sns.barplot(
        x="product_id", 
        y="product_category_name_english", 
        data=most_and_least_products_df.head(5), 
        palette=colors, 
        ax=ax[0],
    )
    ax[0].set_ylabel('')
    ax[0].set_xlabel('')
    ax[0].set_title("products with the highest sales", loc="center", fontsize=18)
    ax[0].tick_params(axis ='y', labelsize=15)

    sns.barplot(
        x="product_id", 
        y="product_category_name_english", 
        data=most_and_least_products_df.sort_values(by="product_id", ascending=True).head(5), 
        palette=colors, 
        ax=ax[1],)
    ax[1].set_ylabel('')
    ax[1].set_xlabel('')
    ax[1].invert_xaxis()
    ax[1].yaxis.set_label_position("right")
    ax[1].yaxis.tick_right()
    ax[1].set_title("products with the lowest sales", loc="center", fontsize=18)
    ax[1].tick_params(axis='y', labelsize=15)

    plt.suptitle("most and least sold products", fontsize=20)
    st.pyplot(fig)

    st.subheader('Detail Performa Produk ')
    with st.expander('Lihat Detail Performa Produk'):
        st.dataframe(most_and_least_products_df)

    with st.expander("Lihat Penjelasan"):
        st.write(
        """Grafik yang ditampilkan menunjukkan produk-produk dengan penjualan tertinggi dan terendah di sebuah platform e-commerce. Produk dengan penjualan tertinggi adalah kategori "bed_bath_table" dengan jumlah penjualan mencapai 11.988 unit, diikuti oleh kategori "health_beauty" dan "sports_leisure". Hal ini menunjukkan bahwa produk-produk yang berkaitan dengan perawatan rumah tangga dan kesehatan cenderung memiliki permintaan yang tinggi di kalangan konsumen. Faktor seperti kebutuhan sehari-hari, kenyamanan, dan kesehatan mungkin berkontribusi pada popularitas kategori-kategori ini."""
        )
        st.write(
        """Di sisi lain, produk dengan penjualan terendah adalah kategori "security_and_services" yang hanya terjual sebanyak 2 unit, diikuti oleh "fashion_childrens_clothes" dan "cds_dvds_musicals". Penjualan yang rendah dalam kategori-kategori ini bisa disebabkan oleh berbagai faktor, termasuk kurangnya promosi, segmentasi pasar yang sempit, atau rendahnya kebutuhan konsumen terhadap produk-produk tersebut. Data ini dapat menjadi dasar bagi perusahaan untuk meninjau kembali strategi pemasaran dan manajemen stok, guna meningkatkan penjualan produk-produk yang kurang laris dan memaksimalkan keuntungan dari produk yang lebih diminati."""
        )

elif selected == "Status Pesanan":
    # ========================================================================================
    # ============================= Status Pesanan ===============================
    # ========================================================================================
    st.header('Bagaimana distribusi biaya pengiriman (freight value) mempengaruhi keputusan pembelian dan tingkat pembatalan pesanan (order status)? apakah biaya pengiriman menyebabkan customer membatalkan pesanannya?')
    st.subheader("Status Pesanan")

    
    plt.figure(figsize=(8, 6))
    sns.barplot(x='order_status', y='freight_value', data=avg_freight_by_status.sort_values(by='freight_value', ascending=False).head(7))
    plt.title('Rata-rata Biaya Pengiriman per Status Pesanan')
    plt.xlabel('Order Status')
    plt.ylabel('Rata-rata Freight Value')
    st.pyplot(plt)


    st.subheader('Jumlah pesanan untuk tiap freight value ')
    with st.expander('Lihat Detail'):
        st.dataframe(freight_status_group.sort_values(by='count', ascending=False).head(10))

    st.subheader('Rata - Rata Biaya pengiriman per pesanan ')
    with st.expander('Lihat Detail'):
        st.write(items_orders_df['freight_value'].mean())
        st.write("Rata-rata biaya pengiriman per pesanan: {:.2f}".format(average_freight_per_order))
        st.write("Tingkat pembatalan pesanan: {:.2f}".format(cancellation_rate, "%"))
        st.write("Dari data ini dapat disimpulkan bahwa Rata-rata biaya pengiriman yang cukup tinggi, berdampak pada tingkat pembatalan orderan yang tinggi juga, bahkan hampir sama dengan status pesanan yang terkirim. kedepannya management bisa mengurangi biaya-biaya pengiriman dengan cara promo free ongkir dan bekerjasama dengan expedisi-expedisi untuk program free ongkir ini agar tingkat pembatalan pesanan menjadi berkurang. dan bisa dilihat juga TOP 10 Delivered itu biaya pengirimannya dibawah rata-rata semua")

    st.subheader('Detail Status Pesanan ')
    with st.expander('Lihat Detail Status Pesanan'):
        st.dataframe(avg_freight_by_status.sort_values(by='freight_value',ascending=False).head(7))

    with st.expander("Lihat Penjelasan"):
        st.write(
        """Dari data dan visualisasi yang ada dapat kita simpulkan bahwa Rata-rata biaya pengiriman untuk pesanan yang dibatalkan(canceled) lebih tinggi daripada yang "approved", yang mungkin menunjukkan bahwa biaya pengiriman yang lebih tinggi bisa berpengaruh terhadap keputusan pembatalan pesanan. Rata-rata biaya pengiriman untuk pesanan yang berhasil dikirim (delivered) relatif tinggi, mendekati rata-rata biaya pengiriman pesanan yang dibatalkan disini terlihat bahwa besarnya pembatalan hampir sama porsinya dengan barang yang berhasil dikirim, yang artinya besar pula kesempatan profit ecommerce tersebut hilang. status processing menunjukkan biaya pengiriman tertinggi, yang mungkin disebabkan oleh penanganan khusus atau logistik yang lebih kompleks dari barang-barang pada umumnya."""
        )
        st.write(
        """action : mengurangi biaya pengiriman agar barang-barang yang terjual lebih tinggi dan meminimalisir customer batal untuk membeli dengan Menyesuaikan strategi harga atau subsidi pengiriman. Pengiriman adalah faktor penting dalam keputusan pembelian, yang dapat mempengaruhi profit dan kepuasan pelanggan"""
        )

elif selected == "Waktu Pengiriman":
    # ========================================================================================
    # ============================= Waktu Pengiriman =========================================
    # ========================================================================================
    st.header('Bagaimana hubungan antara lokasi geografis pelanggan dan waktu pengiriman, kota apa yang terlama pengirimannya dan berapa hari waktu pengiriman yang meleset dari estimasi pengiriman?')
    st.subheader("Waktu Pengiriman")
    fig, ax = plt.subplots(figsize=(10, 6))
    top_10_cities.plot(kind='bar', ax=ax)
    ax.set_title('Top 10 Customer Cities by Average Delivery Time Difference')
    ax.set_xlabel('Customer City')
    ax.set_ylabel('Average Delivery Time Difference (days)')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=50)

    st.pyplot(fig)

    st.subheader('Detail Waktu Pengiriman ')
    with st.expander('Lihat Detail Waktu Pengiriman'):
        st.dataframe(avg_delivery_time_diff_by_city.sort_values(ascending=False).head(10))

    with st.expander("Lihat Penjelasan"):
        st.write(
        """pada visualisasi data dapat terlihat kota Juruti menjadi kota yang terlama dalam hal pengiriman barang dan meleset/melenceng jauh dari estimasi/perkiraan waktunya hampir mendekati 60 hari, ini bisa mejadi perhatian untuk ecommerce dalam hal pengiriman barang ke 10 kota tersebut yang rata - rata tingkat melesetnya sangat tinggi."""
        )
        st.write(
        """Action : mengevaluasi dan mengaudit area geografis di mana waktu pengiriman yang sering terlambat tersebut agar rentan waktu dari estimasi dan waktu pengiriman yang sebenarnya menjadi lebih pendek. Menambah Distributor/rekanan di atau pada 10 kota tersebut untuk membantu pendistribusian barang lebih cepat. mengevaluasi manajement rantai pasok yang sudah berjalan. meninjau kembali estimasi/perkiraan waktu pada 10 kota tersebut.Mengetahui di mana masalah pengiriman terjadi dapat meningkatkan kepuasan pelanggan yang dimana nantinya akan berdampak pada profit ecommerce itu juga."""
        )

    # ========================================================================================
    # ======================================== RFM Analisis ==================================
    # ========================================================================================
elif selected == "RFM Analisis":
    st.header('Bagaimana RFM Analisisnya?')    
    st.subheader("RFM Best Value")

    colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

    tab1, tab2, tab3 = st.tabs(["Recency", "Frequency", "Monetary"])

    with tab1:
        plt.figure(figsize=(16, 8))
        sns.barplot(
            y="Recency", 
            x="customer_id", 
            data=rfm.sort_values(by="Recency", ascending=True).head(5), 
            palette=colors,
        )
        plt.title("By Recency (Day)", loc="center", fontsize=18)
        plt.ylabel('')
        plt.xlabel("customer")
        plt.tick_params(axis ='x', labelsize=15)
        plt.xticks([])
        st.pyplot(plt)

    with tab2:
        plt.figure(figsize=(16, 8))
        sns.barplot(
            y="Frequency", 
            x="customer_id", 
            data=rfm.sort_values(by="Frequency", ascending=False).head(5), 
            palette=colors,
        )
        plt.ylabel('')
        plt.xlabel("customer")
        plt.title("By Frequency", loc="center", fontsize=18)
        plt.tick_params(axis ='x', labelsize=15)
        plt.xticks([])
        st.pyplot(plt)

    with tab3:
        plt.figure(figsize=(16, 8))
        sns.barplot(
            y="Monetary", 
            x="customer_id", 
            data=rfm.sort_values(by="Monetary", ascending=False).head(5), 
            palette=colors,
        )
        plt.ylabel('')
        plt.xlabel("customer")
        plt.title("By Monetary", loc="center", fontsize=18)
        plt.tick_params(axis ='x', labelsize=15)
        plt.xticks([])
        st.pyplot(plt)

    with st.expander("Lihat Penjelasan"):
        st.subheader("Recency:")
        st.dataframe(rfm.sort_values(by='Recency',ascending=True).head(10))
        st.write(
        """yang tidak masuk dalam kategori ini kemungkinan mereka tidak aktif lagi dalam jangka waktu yang lama, sehingga perlu adanya upaya reaktivasi, seperti kampanye pemasaran yang menargetkan mereka secara spesifik."""
        )
        st.subheader("Frequency:")
        st.dataframe(rfm.sort_values(by='Frequency',ascending=False).head(10))
        st.write(
        """Top 10 customer yang sering bertransaksi adalah pelanggan yang sangat loyal dan kemungkinan besar memberikan kontribusi signifikan terhadap pendapatan perusahaan. Perusahaan harus mempertimbangkan strategi untuk mempertahankan pelanggan ini, seperti program loyalitas atau penawaran khusus."""
        )
        st.subheader("Monetary:")
        st.dataframe(rfm.sort_values(by='Monetary',ascending=False).head(10))
        st.write(
        """Top 10 customer dengan total pengeluaran/belanja terbesar" (Monetary tinggi) adalah pelanggan yang paling bernilai bagi perusahaan. Mereka memberikan pendapatan terbesar dan karenanya perusahaan harus mempertimbangkan untuk menawarkan layanan premium atau penawaran eksklusif untuk meningkatkan kepuasan mereka."""
        )
