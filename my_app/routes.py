from flask import render_template, url_for, redirect
from .forms import SearchForm
from .web_crawler import print_test, get_reviews

import os
import secrets
from my_app import application

#reviews = {'a': [{'title': 'abc', 'url': 'url1'}, {'title': 'aabc', 'url': 'url11'}], 
#           'b': [{'title': 'abcd', 'url': 'url2'}, {'title': 'abcde', 'url': 'url22'}]}

import boto3
from boto3.dynamodb.conditions import Key, Attr

DB_TABLE_NAME = application.config['DYNAMODB_TABLE']
DB_REGION_NAME = application.config['DYNAMODB_REGION']
ACCESS_KEY = application.config['DYNAMODB_KEY']
SECRET_KEY = application.config['DYNAMODB_SECRET']

dynamodb_client = boto3.client('dynamodb',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=DB_REGION_NAME
)
scan_paginator = dynamodb_client.get_paginator('scan')

# Get the service resource.
DB = boto3.resource('dynamodb', region_name=DB_REGION_NAME)
DB_TABLE = DB.Table(DB_TABLE_NAME)
Primary_Partition_Key = 'book'
Primary_Sort_Key = 'id'

# http, https
HTTP = application.config['HTTP_SSL']

# User Page
@application.route('/', methods=['GET', 'POST'])
@application.route('/home', methods=['GET', 'POST'])
def home():    
    form = SearchForm()
    home_image = url_for('static', filename='images/home.png')
    about_image = url_for('static', filename='images/about.png')
    logo_image = url_for('static', filename='images/trevari_logo.png')

    if form.validate_on_submit():
        search_word = form.book_title.data
        return redirect(url_for('search_books', search_word=search_word, _external=True, _scheme=HTTP))

    return render_template('home.html', form=form, title='Home', logo_image=logo_image, home_image=home_image, about_image=about_image)

@application.route('/<string:search_word>/search_books', methods=['GET', 'POST'])
def search_books(search_word):
    form = SearchForm()
    home_image = url_for('static', filename='images/home.png')
    about_image = url_for('static', filename='images/about.png')
    logo_image = url_for('static', filename='images/trevari_logo.png')

    if form.validate_on_submit():
        search_word = form.book_title.data
        return redirect(url_for('search_books', search_word=search_word, _external=True, _scheme=HTTP))

    # AWS DynamoDB
    operation_parameters = {
        'TableName': DB_TABLE_NAME,
        'ScanFilter': {
            Primary_Partition_Key: {
                'AttributeValueList': [
                    {'S': search_word}
                ],
                'ComparisonOperator': 'CONTAINS'
            }
        }
    }   
    items = []
    page_iterator = scan_paginator.paginate(**operation_parameters) 
    for page in page_iterator:
        cur_pageItems = page['Items']
        #print(cur_pageItems)
        if cur_pageItems:
            items += cur_pageItems

    #print(items)
    #print("total:", len(items))
    
    #response = DB_TABLE.scan(
    #    FilterExpression = Attr(Primary_Partition_Key).contains(search_word)
    #)
    
    #items = response['Items']
    #print(items)
    book_title_list = [item[Primary_Partition_Key]['S'] for item in items]
    #print(book_title_list)
    book_title_list = list(set(book_title_list))# 중복 제거

    return render_template('home.html', form=form, title='도서 검색 결과', 
                            logo_image=logo_image,
                            home_image=home_image, about_image=about_image,
                            books=book_title_list)

@application.route('/<string:book_title>/result_reviews', methods=['GET', 'POST'])
def result_reviews(book_title):
    form = SearchForm()
    home_image = url_for('static', filename='images/home.png')
    about_image = url_for('static', filename='images/about.png')
    logo_image = url_for('static', filename='images/trevari_logo.png')

    if form.validate_on_submit():
        search_word = form.book_title.data
        return redirect(url_for('search_books', search_word=search_word, _external=True, _scheme=HTTP))

    # AWS DynamoDB
    response = DB_TABLE.query(
        KeyConditionExpression = Key(Primary_Partition_Key).eq(book_title)
    )
    items = response['Items']
    #print(items)
    base_url = "https://trevari.co.kr/bookreviews/show?id="
    return render_template('home.html', form=form, title=book_title,
                            logo_image=logo_image, home_image=home_image, about_image=about_image,
                            reviews=items, review_url=base_url)

@application.route('/about')
def about():
    home_image = url_for('static', filename='images/home.png')
    about_image = url_for('static', filename='images/about.png')
    logo_image = url_for('static', filename='images/trevari_logo.png')

    return render_template('about.html', title='About',
                            logo_image=logo_image, home_image=home_image, about_image=about_image)

@application.route('/call_crawler')
def call_crawler():
    #a = print_test()
    #print(a)

    reviews = get_reviews()
    books = reviews.keys()

    # 파일에 쓰기
    #f = open("reviews.txt", 'w', encoding='UTF8')
    #for book in books:
    #    current_book_reviews = reviews[book]
    #    for review in current_book_reviews:
    #        data = book + '%' + review['url'] + '%' + review['title'] + '\n'
    #        f.write(data)
    #f.close()

    #print(reviews)
    with DB_TABLE.batch_writer(overwrite_by_pkeys=[Primary_Partition_Key, Primary_Sort_Key]) as batch:
        for book in books:
            current_book_reviews = reviews[book]
            for review in current_book_reviews:
                #print('book:', book)
                #print('url:', review['url'])
                #print('title:', review['title'])
                batch.put_item(
                    Item={
                        Primary_Partition_Key: book,
                        Primary_Sort_Key: review['url'].split('?id=')[1],
                        'title': review['title']
                    }
                )
              
    return redirect(url_for('home'))