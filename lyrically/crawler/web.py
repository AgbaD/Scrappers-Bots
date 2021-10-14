#!usr/bin/python3

import re
import requests
from bs4 import BeautifulSoup


base_url = "https://genius.com/"


def get_page(url):
    resp = requests.get(url)
    return BeautifulSoup(resp.content, "html.parser")


def get_article(link):
    resp = get_page(link)
    article = resp.find("div", class_="article_rich_text_formatting").get_text()
    return re.sub(r'[\(\[].*?[\)\]]', '', article)


def get_mt():   # mt = main_title
    home = get_page(base_url)
    mt_div = home.find("div", class_="EditorialPlacement__Title-sc-1kp33kw-1 bMPUfx")
    return mt_div.find('h2').text.strip()


def get_ml():   # ml = main_link
    home = get_page(base_url)
    ml_tag = home.find("a", class_="EditorialPlacement__Link-sc-1kp33kw-2 eCAFYK")
    return ml_tag["href"]


def get_ma():   # ma = main article
    link = get_ml()
    article = get_article(link)
    return article


def get_ot():   # ot = other_titles
    home = get_page(base_url)
    ot_divs = home.find_all('div', class_="EditorialPlacement__Title-sc-1kp33kw-1 dgdgAp")
    ot = [t.find('h2').text.strip() for t in ot_divs]
    return ot


def get_ol():   # ol = other_links
    home = get_page(base_url)
    ol_par = home.find_all('a', class_="EditorialPlacement__Link-sc-1kp33kw-2 kzXgsm")
    ol = [link["href"] for link in ol_par]
    return ol


def get_oa():   # ol = other_articles
    ol = get_ol()
    oa = [get_article(link) for link in ol]
    return oa


def get_main():
    link = get_ml()
    title = get_mt()
    article = get_ma()
    return link, title, article


def get_others():
    links = get_ol()
    titles = get_ot()
    articles = get_oa()
    return links, titles, articles


def get_chart():
    home = get_page(base_url)
    chart = []
    chart_links = get_chart_links(home)
    chart_titles = get_chart_titles(home)
    chart_artists = get_chart_artists(home)

    for j in range(len(chart_titles)):
        a = (chart_titles[j], chart_links[j], chart_artists[j])
        chart.append(a)
    return chart


def get_chart_titles(home):
    titles = home.find_all("div", class_="ChartSongdesktop__Title-sc-18658hh-3 fODYHn")
    titles = [t.text.strip() for t in titles]
    return titles


def get_chart_artists(home):
    artists = home.find_all("h4", class_="ChartSongdesktop__Artist-sc-18658hh-5 kiggdb")
    artists = [artist.text.strip() for artist in artists]
    return artists


def get_chart_links(home):
    links = home.find_all("a", class_="PageGriddesktop-a6v82w-0 ChartItemdesktop__Row-sc-3bmioe-0 qsIlk")
    links = [link["href"] for link in links]
    return links

