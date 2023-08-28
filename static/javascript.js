document.getElementById('searchInput').addEventListener('keydown',(e)=>{
    if(e.key === 'Enter'){
        document.getElementById('submit').click()
    }
})
var pages={0:{}}
var currentPage=0
function Filter(data){
    let cp=0,cn=0;
    for(let i of Object.keys(data)){
        if (parseFloat(data[i][0]) > 0) {
            pages[0][cp] = data[i]
            cp+=1
        }
    }
}
var time=0,tot=0
async function search(){
    const timest = performance.now()
    const res = await fetch(`http://127.0.0.1:5000/search?q=${document.getElementById('searchInput').value}`)
    const v = await res.json()
    console.log(v)
    await Filter(v)
    tot=Object.keys(pages[0]).length
    const timeend = performance.now()
    time=Math.round((timeend-timest)*1000)/1000000
    document.getElementById('results').innerText=''
    displayTime()
    displayPage(0)
}

function displayTime(){
    let cv = document.createElement('label')
    cv.style.borderRadius='50px'
    cv.style.color='#040410'
    cv.style.border = '1px #90A4AE solid'
    cv.style.padding= '5px 10px'
    cv.innerText=`About ${tot} results (${time}s)`
    cv.style.margin = '5px'
    document.getElementById('results').appendChild(cv)
}
function displayPage(pageNo){
    let v = pages[pageNo]
    for( let i of Object.keys(v)){
        let div = document.createElement('div')
        div.className='searchClass'
        let content = document.createElement('a')
        let lnk = document.createElement('p')
        content.style.color='#1666C7'
        content.href=v[i][1]
        content.innerText=v[i][2].substr(0,100)
        content.style.overflowWrap='break-word'
        content.target = '_blank'
        content.style.textDecoration='none'
        lnk.style.color='#040410'
        lnk.style.textDecoration='underline'
        lnk.style.fontSize='medium'
        lnk.innerText = v[i][1]
        div.append(content,lnk)
        document.getElementById('results').appendChild(div)
    }
}
