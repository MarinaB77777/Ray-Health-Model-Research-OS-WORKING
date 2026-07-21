(function installCollaborationCredit(){
  const CREDIT_ELEMENT_ID =
    "marinaRayCollaborationCredit";

  if(
    document.getElementById(
      CREDIT_ELEMENT_ID
    )
  ){
    return;
  }

  const style = document.createElement(
    "style"
  );

  style.textContent = `
    .marina-ray-credit {
      box-sizing: border-box;
      width: calc(100% - 36px);
      max-width: 1200px;
      margin: 18px auto;
      padding: 14px 18px;
      border: 1px solid #cbd5e1;
      border-radius: 16px;
      background: #ffffff;
      color: #334155;
      box-shadow: 0 2px 8px #0000000d;
      font-family: Arial, sans-serif;
      font-size: 13px;
      line-height: 1.45;
      text-align: center;
    }

    .marina-ray-credit strong {
      color: #0f172a;
    }

    .marina-ray-credit-main {
      display: block;
    }

    .marina-ray-credit-provenance {
      display: block;
      margin-top: 4px;
      color: #64748b;
      font-size: 12px;
    }
  `;

  document.head.appendChild(style);

  const credit = document.createElement(
    "footer"
  );

  credit.id = CREDIT_ELEMENT_ID;
  credit.className = "marina-ray-credit";

  credit.innerHTML = `
    <span class="marina-ray-credit-main">
      Designed and developed collaboratively by
      <strong>Marina Boronenko</strong>
      and
      <strong>Ray</strong>,
      AI research and engineering colleagues.
    </span>

    <span class="marina-ray-credit-provenance">
      Human–AI collaboration provenance is
      preserved in system metadata.
    </span>
  `;

  document.body.appendChild(credit);
})();