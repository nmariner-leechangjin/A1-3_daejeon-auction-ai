const form=document.getElementById("auction-form");
const resultBox=document.getElementById("result-box");
const aiButton=document.getElementById("ai-opinion-button");
const aiBox=document.getElementById("ai-opinion-box");
const formMessage=document.getElementById("form-message");
let analysisData=null;

const value=id=>document.getElementById(id).value.trim();
const numberValue=id=>Number(value(id));
const formatWon=price=>Math.round(price).toLocaleString("ko-KR")+"원";

form.addEventListener("submit",event=>{
  event.preventDefault();
  formMessage.textContent="";
  aiButton.disabled=true;
  aiBox.textContent="AI 종합의견을 요청하면 이곳에 표시됩니다.";

  const appraisalPrice=numberValue("appraisal-price");
  const minimumPrice=numberValue("minimum-price");
  const kbPrice=numberValue("kb-price");
  const failedCount=numberValue("failed-count")||0;
  const views=numberValue("views")||0;

  if(appraisalPrice<=0||minimumPrice<=0||kbPrice<=0){
    formMessage.textContent="감정가, 최저가, KB시세를 모두 0보다 큰 숫자로 입력해주세요.";
    resultBox.textContent="필수 입력값을 확인해주세요.";
    analysisData=null;
    return;
  }
  if(failedCount<0||views<0){
    formMessage.textContent="유찰 횟수와 조회수는 0 이상이어야 합니다.";
    analysisData=null;
    return;
  }

  const appraisalRate=(minimumPrice/appraisalPrice)*100;
  const kbRate=(minimumPrice/kbPrice)*100;
  let competition="낮음";
  let competitionRate=0;
  if(views>=1000){competition="매우 높음";competitionRate=.06}
  else if(views>=500){competition="높음";competitionRate=.04}
  else if(views>=200){competition="보통";competitionRate=.02}

  let recommendedBid=kbPrice*.70*(1+competitionRate);
  recommendedBid=Math.max(recommendedBid,minimumPrice);
  const lowBid=recommendedBid*.98;
  const highBid=recommendedBid*1.02;
  let attractiveness="낮음";
  if(kbRate<=60)attractiveness="매우 높음";
  else if(kbRate<=70)attractiveness="높음";
  else if(kbRate<=80)attractiveness="보통";

  analysisData={
    case_number:value("case-number"),
    apartment_name:value("apartment-name"),
    address:value("address"),
    appraisal_price:appraisalPrice,
    minimum_price:minimumPrice,
    kb_price:kbPrice,
    failed_count:failedCount,
    views,
    appraisal_rate:Number(appraisalRate.toFixed(1)),
    kb_rate:Number(kbRate.toFixed(1)),
    price_attractiveness:attractiveness,
    competition,
    low_bid:Math.round(lowBid),
    high_bid:Math.round(highBid)
  };

  resultBox.innerHTML="<strong>경매 기초 분석</strong><br><br>"+
    "감정가 대비 최저가: "+appraisalRate.toFixed(1)+"%<br>"+
    "KB시세 대비 최저가: "+kbRate.toFixed(1)+"%<br>"+
    "유찰 횟수: "+failedCount+"회<br>"+
    "마이옥션 조회수: "+views.toLocaleString("ko-KR")+"회<br><br>"+
    "<strong>가격 매력도</strong><br>"+attractiveness+"<br><br>"+
    "<strong>예상 경쟁도</strong><br>"+competition+"<br><br>"+
    "<strong>프로그램 권장 입찰 범위</strong><br>"+formatWon(lowBid)+" ~ "+formatWon(highBid)+
    "<br><br><small>※ 참고용 분석입니다. 실제 입찰 전 권리분석, 점유관계와 명도비용을 별도로 확인하세요.</small>";

  aiButton.disabled=false;
  resultBox.scrollIntoView({behavior:"smooth",block:"nearest"});
});

aiButton.addEventListener("click",async()=>{
  if(!analysisData){
    aiBox.textContent="먼저 입찰가 분석을 실행해주세요.";
    return;
  }

  const controller=new AbortController();
  const timeoutId=setTimeout(()=>controller.abort(),60000);
  aiButton.disabled=true;
  aiButton.textContent="AI 분석 중...";
  aiBox.textContent="AI가 계산 결과를 분석하고 있습니다. 최대 60초 정도 걸릴 수 있습니다.";

  try{
    const response=await fetch("/api/recommend",{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify(analysisData),
      signal:controller.signal
    });
    const contentType=response.headers.get("content-type")||"";
    if(!contentType.includes("application/json")){
      throw new Error("서버가 올바른 응답을 보내지 않았습니다.");
    }
    const result=await response.json();
    if(!response.ok)throw new Error(result.error||"AI 분석에 실패했습니다.");
    if(!result.result)throw new Error("AI 분석 결과가 비어 있습니다.");
    aiBox.textContent=result.result;
  }catch(error){
    aiBox.textContent=error.name==="AbortError"
      ?"AI 응답이 늦어 요청을 중단했습니다. 잠시 후 다시 시도해주세요."
      :"AI 분석 오류: "+error.message;
  }finally{
    clearTimeout(timeoutId);
    aiButton.disabled=false;
    aiButton.textContent="Gemini AI 종합의견 다시 받기";
  }
});