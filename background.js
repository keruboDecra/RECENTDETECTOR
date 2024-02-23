chrome.contextMenus.create({
  id: "check-cyberbully",
  title: "Detect Cyberbullying",
  contexts: ["selection"],
});

chrome.contextMenus.onClicked.addListener(async function (info, tab) {
  console.log(info);
  if (info.menuItemId === "check-cyberbully") {
    console.log(info.selectionText);
    const formData = new FormData();
    formData.append("user_input", info.selectionText);

    const response = await fetch(
      "https://detection-main-production.up.railway.app/detect",
      {
        method: "POST",
        body: formData,
      }
    );
    const data = await response.json();
    console.log(data?.details);
    const isOffensive = data?.details?.offensive;
    const reasons = data?.details?.offensive_reasons;
    // chrome.tabs.sendMessage(tab.id, { result: data });

    // open pop up
    chrome.windows.create({
      url: "popup.html",
      type: "popup",
      width: 500,
      height: 800,
      top: 100,
      left: 100,
    });

    setTimeout(async () => {
      // send the data to the popup via content script message
      const [tab] = await chrome.tabs.query({
        active: true,
        lastFocusedWindow: true,
      });
      console.log(tab);
      const resp = await chrome.tabs.sendMessage(tab.id, {
        isOffensive,
        reasons,
      });
      // do something with response here, not outside the function
      console.log(resp);
    }, 2000);
  }
});
