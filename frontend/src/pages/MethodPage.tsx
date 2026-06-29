import katex from "katex";
import "katex/dist/katex.min.css";
import { useMemo } from "react";

export default function MethodPage() {
  return (
    <article className="mx-auto max-w-2xl pb-32">
      <Hero />
      <Chapter num="01" title="為什麼要預測「年度變動率」">
        <P>
          消費者物價指數（Consumer Price Index, CPI）是觀察民生物價變動的重要統計，其中食物類價格
          更直接影響家計支出、通膨感受與政策溝通。一般新聞或分析常關注
          「當月年增率」，亦即「本月指數對去年同月指數」的變動。
        </P>
        <P>
          然而，政府正式公布的<Strong>整年物價變動</Strong>並非單一月份，而
          是「全年十二個月平均指數，相對前一年全年平均指數的變動」。換言之，
          若要在年初或年中判斷「今年食物價格平均將比去年高多少」，就必須同時
          處理<Strong>已知月份</Strong>（實際 CPI）與
          <Strong>尚未發生的月份</Strong>（需要預測）。
        </P>
        <P>
          令 <TeXInline>{String.raw`I_{t,m}`}</TeXInline> 為某類別在年度{" "}
          <TeXInline>{String.raw`t`}</TeXInline> 之第{" "}
          <TeXInline>{String.raw`m`}</TeXInline>{" "}
          月的 CPI，年度平均定義為
          <TeXInline>{String.raw`\bar{I}_{t} = \tfrac{1}{12}\sum_{m=1}^{12} I_{t,m}`}</TeXInline>
          。當年度十二個月皆已公布時，年變動率為：
        </P>
        <TeXBlock>{String.raw`\Delta I_{t} \;=\; \frac{\bar{I}_{t} - \bar{I}_{t-1}}{\bar{I}_{t-1}} \times 100\%`}</TeXBlock>
        <P>
          當年度尚未結束，未公布的月份必須以模型預測補上。本平台的核心即
          提供一套<Strong>透明、可重現、可逐月更新</Strong>的預測流程，並透過
          95% 預測區間表達不確定性。
        </P>
      </Chapter>

      <Chapter num="02" title="為什麼要逐月推進?">
        <P>
          年初時，十二個月中多數資料尚未公布，預測不確定性自然較高；隨著
          月份推進，已知資料逐月增加，剩餘未知月份減少，
          <Strong>預測區間應逐步收斂</Strong>。
        </P>
        <P>
          若預測方法無法呈現這個「不確定性遞減」的過程，使用者容易把點預測
          誤認為確定結果，或低估未來的物價波動風險。
        </P>
        <P>
          以「截至年度 <TeXInline>{String.raw`t`}</TeXInline> 第{" "}
          <TeXInline>{String.raw`T`}</TeXInline> 月」之資訊預測該年年變動率
          時，先把當年已公布的 1 至 <TeXInline>{String.raw`T`}</TeXInline>{" "}
          月實際 CPI 與模型對第
          <TeXInline>{String.raw`T+1`}</TeXInline> 至{" "}
          <TeXInline>{String.raw`12`}</TeXInline>{" "}
          月的預測 <TeXInline>{String.raw`\hat{I}_{t,m}`}</TeXInline> 合併為
          當年「混合年度平均」：
        </P>
        <TeXBlock>{String.raw`\hat{\bar{I}}_{t \mid T} \;=\; \frac{1}{12}\left(\, \sum_{m=1}^{T} I_{t,m} \;+\; \sum_{m=T+1}^{12} \hat{I}_{t,m} \,\right)`}</TeXBlock>
        <P>再以前一年實際年平均為基期，得到逐月推進的年變動率預測：</P>
        <TeXBlock>{String.raw`\widehat{\Delta I}_{t \mid T} \;=\; \frac{\hat{\bar{I}}_{t \mid T} - \bar{I}_{t-1}}{\bar{I}_{t-1}} \times 100\%`}</TeXBlock>
        <P>
          因此，本平台對每一個類別都會做共 12 個月的滾動預測
          （自前一年 12 月起至本年 11 月），各使用該時點之前的近 12 年歷史
          資料重新配適模型。「年度 YoY 滾動預測」分頁中，每一個 X 軸點都
          對應一個獨立模型的結果。
        </P>
      </Chapter>

      <Chapter num="03" title="模型與方法">
        <Sub>3.1　資料來源</Sub>
        <P>
          行政院主計總處{" "}
          消費者物價指數月資料
          （<Link href="https://data.gov.tw/dataset/6019">dataset 6019</Link>），基期民國 110 年=100。
        </P>

        <Sub>3.2　訓練窗口</Sub>
        <P>
          每個預測時點僅使用<Strong>近 12 年（144 個月）</Strong>歷史 CPI，
          避免遠期結構性變化干擾。例如「截至 2026 年 4 月」之預測，使用
          2014 年 5 月至 2026 年 4 月共 144 個月配適。
        </P>

        <Sub>3.3　模型結構（SARIMA）</Sub>
        <P>
          以可納入<Strong>季節性</Strong>之 SARIMA（Seasonal AutoRegressive
          Integrated Moving Average）處理 CPI 序列的自我相關、趨勢與 12 月
          循環。食品價格常具有季節循環：蔬果受產季與天候影響、蛋品受供需
          週期影響，月資料之間並非獨立。模型結構表示為：
        </P>
        <TeXBlock>{String.raw`\mathrm{SARIMA}(p,d,q)(P,D,Q)_{12}`}</TeXBlock>

        <Sub>3.4　選模準則</Sub>
        <P>
          以<Strong>貝氏資訊準則（BIC）</Strong>透過{" "}
          <Code>pmdarima.auto_arima</Code> 以 stepwise 方式搜尋最佳階數
          <TeXInline>{String.raw`(p,d,q)(P,D,Q)_{12}`}</TeXInline>。BIC 同時
          懲罰模型複雜度，降低過度配適風險：
        </P>
        <TeXBlock>{String.raw`\mathrm{BIC} \;=\; k\,\ln(n) \;-\; 2\,\ln(\hat{L})`}</TeXBlock>

        <Sub>3.5　蒙地卡羅模擬</Sub>
        <P>
          模型配適後，使用 <Code>SARIMAXResults.simulate</Code>
          （seed=1、anchor=&quot;end&quot;）生成
          <Strong> 10,000 條未來路徑</Strong>，索引為{" "}
          <TeXInline>{String.raw`s = 1, 2, \ldots, S`}</TeXInline>，其中{" "}
          <TeXInline>{String.raw`S = 10{,}000`}</TeXInline>，第{" "}
          <TeXInline>{String.raw`s`}</TeXInline> 條路徑記為
          <TeXInline>{String.raw`\hat{I}^{(s)}_{t,m}`}</TeXInline>
          。每條代表「在估計誤差分布下的一種可能未來」。
        </P>

        <Sub>3.6　結合實際與模擬</Sub>
        <P>
          對每一條路徑 <TeXInline>{String.raw`s`}</TeXInline>{" "}
          計算其對應的年變動率
          <TeXInline>{String.raw`\widehat{\Delta I}^{(s)}_{t \mid T}`}</TeXInline>
          ，再對 10,000 條取分位數，得到中位數預測與 95% 預測區間：
        </P>
        <TeXBlock>{String.raw`\bigl[\, q_{0.025},\; q_{0.500},\; q_{0.975} \,\bigr] \;=\; \mathrm{Quantile}\!\left(\, \bigl\{ \widehat{\Delta I}^{(s)}_{t \mid T} \bigr\}_{s=1}^{S} \,\right)`}</TeXBlock>
      </Chapter>

      <Chapter num="04" title="平台輸出">
        <Sub>4.1　月度 CPI 水準</Sub>
        <P>
          歷史指數（黑線）加上未來 18 個月預測中位數（紫線），以及 95% 預測
          區間（淡紫帶狀區）。
        </P>
        <Sub>4.2　年度 YoY 滾動預測</Sub>
        <P>
          X 軸為「使用資料截至時點」（12 月、1 月…11 月），Y 軸為預測該年
          年度變動率分位數。前段月份反映模型在不同資訊量下的判斷如何收斂。
        </P>
        <Sub>4.3　下個月上漲機率</Sub>
        <P>取 10,000 條路徑中，下月模擬值超過最新實際值的比例：</P>
        <TeXBlock>{String.raw`P_{\uparrow} \;=\; \frac{1}{S}\sum_{s=1}^{S} \mathbf{1}\!\left(\, \hat{I}^{(s)}_{t,\,m+1} \;>\; I_{t,m} \,\right)`}</TeXBlock>
        <Sub>4.4　月報 xlsx 下載</Sub>
        <P>
          參考 USDA Food Price Outlook 每月報表，含 14 類別的月變動率、年變動率、年初至今
          平均、歷年年度變動率與當年度 95% 預測區間，可直接用於對外溝通或
          內部報告。
        </P>
      </Chapter>

      <Chapter num="05" title="14 項食物類目">
        <P>本平台預測之 14 項對應主計總處公布之消費者物價基本分類項目：</P>
        <P>
          食物類、外食費、肉類、豬肉、牛肉（含牛內臟）、雞肉、水產品、蛋類、
          雞蛋、乳類、鮮乳、蔬菜、水果、食用油。
        </P>
      </Chapter>

      <Chapter num="06" title="限制與注意事項">
        <P>
          波動越大的類別（如蔬菜、水果、蛋類），年初預測區間越寬，反映短期
          天候與供需衝擊難以預知。隨年內資料公布，區間應快速收斂。
        </P>
        <P>
          模型假設未來誤差結構與過去 12 年類似。若發生重大結構性變化（政策、
          極端天候、貿易事件），實際值可能不落在 95% 預測區間內。
        </P>
        <P>
          「上漲機率」與「中位數」並非確定預測，僅代表在給定模型與假設下的
          條件機率與位置統計。
        </P>
      </Chapter>

      <Chapter num="—" title="參考文獻">
        <P>
          U.S. Department of Agriculture, Economic Research Service (2022).{" "}
          <em>Food Price Outlook: Methodology of Forecasts</em>. Technical
          Bulletin No. 1957（TB-1957）。
        </P>
        <P>
          吳金擇（2026）。
          <em>論如何預測我國食物類消費者物價指數年變動率</em>。農業部統計處。
        </P>
        <P>
          Hyndman, R. J. &amp; Khandakar, Y. (2008). Automatic Time Series
          Forecasting: The forecast Package for R.{" "}
          <em>Journal of Statistical Software</em>, 27(3).
        </P>
      </Chapter>
    </article>
  );
}

// ────────────────────────────────────────────────────────────────────────────
// Layout primitives — 雜誌風單欄、生章節、寬鬆留白
// ────────────────────────────────────────────────────────────────────────────

function Hero() {
  return (
    <header className="pt-12 pb-20 sm:pt-20 sm:pb-32 text-center">
      <p className="text-sm sm:text-base tracking-[0.4em] uppercase text-indigo-600 mb-6 font-semibold">
        Methodology
      </p>
      <h1 className="font-serif text-4xl sm:text-5xl font-bold text-slate-900 leading-tight tracking-tight mb-8">
        食品類物價(指數)預測平台
        <br />
        方法說明
      </h1>
      <p className="font-serif text-[17px] sm:text-lg leading-[1.95] text-slate-500 max-w-xl mx-auto">
        本平台參考美國農業部（USDA）食品價格展望（Food Price Outlook）之
        時間序列方法，建立我國 14 項食物類消費者物價指數（CPI）年變動率的
        逐月預測流程。
      </p>
    </header>
  );
}

function Chapter({
  num,
  title,
  children,
}: {
  num: string;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section className="mt-24 first-of-type:mt-0 pt-12 border-t border-slate-200">
      <div className="flex items-baseline gap-6 mb-12">
        <span className="font-mono text-3xl sm:text-4xl tracking-wider font-bold text-indigo-500">
          {num}
        </span>
        <h2 className="font-serif text-2xl sm:text-3xl font-bold text-slate-900 leading-snug">
          {title}
        </h2>
      </div>
      <div className="space-y-7">{children}</div>
    </section>
  );
}

function Sub({ children }: { children: React.ReactNode }) {
  return (
    <h3 className="font-serif text-lg font-semibold text-slate-800 leading-snug pt-6">
      {children}
    </h3>
  );
}

function P({ children }: { children: React.ReactNode }) {
  return (
    <p className="font-serif text-[17px] leading-[1.95] text-slate-700">
      {children}
    </p>
  );
}

function Strong({ children }: { children: React.ReactNode }) {
  return (
    <strong className="font-semibold text-slate-900 underline decoration-indigo-200 decoration-2 underline-offset-4">
      {children}
    </strong>
  );
}

function Code({ children }: { children: React.ReactNode }) {
  return (
    <code className="mx-0.5 rounded bg-slate-100 px-1.5 py-0.5 font-mono text-[14px] text-slate-800">
      {children}
    </code>
  );
}

function Link({ href, children }: { href: string; children: React.ReactNode }) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noreferrer"
      className="text-indigo-700 underline underline-offset-4 decoration-indigo-300 hover:decoration-indigo-700"
    >
      {children}
    </a>
  );
}

function TeXBlock({ children }: { children: string }) {
  const html = useMemo(
    () =>
      katex.renderToString(children, {
        throwOnError: false,
        displayMode: true,
      }),
    [children],
  );
  return (
    <div
      className="my-10 overflow-x-auto rounded-lg bg-slate-50 px-6 py-6 border border-slate-200/60"
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}

function TeXInline({ children }: { children: string }) {
  const html = useMemo(
    () =>
      katex.renderToString(children, {
        throwOnError: false,
        displayMode: false,
      }),
    [children],
  );
  return <span className="mx-0.5" dangerouslySetInnerHTML={{ __html: html }} />;
}
