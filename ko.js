// this is sample example

const {log} = console

const puppeteer = require('puppeteer');
const cheerio = require('cheerio');

const url = {
    searchWord : (word) => `https://krdict.korean.go.kr/eng/dicMarinerSearch/search?mainSearchWord=${word}`,
}

const selector = {
    path: 'div.search_result > dl',
    items: [
        { name: 'counter', path: 'span.count', text: true, href: false },
        { name: 'href', path: 'span.title > a', text: false, href: true },
        { name: 'title', path: 'span.title > a', text: true, href: false },
        { name: 'nick', path: 'span.global-nick', text: true, href: false },
        { name: 'date', path: 'span.date', text: true, href: false },
    ],
    type: 'post',
};

async function run() {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    await page.goto(url.searchWord("지금"));
    const html = await page.content()
    await page.close();
    await browser.close();
    const $ = cheerio.load(html);
    const r1 = $("div.search_result > dl")
    const r2 = r1.find("span.word_type1_17")

    r2.each((i,e)=>log($(e).text())) 
  }
  
  run();


