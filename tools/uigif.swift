// uigif: load an HTML file offscreen, run setup.js, then n times: run step.js and snapshot to <outdir>/f%03d.png
//   uigif <html> <setup.js> <step.js> <outdir> <n> [w h scale wait]
import Cocoa
import WebKit

let args = CommandLine.arguments
guard args.count >= 6 else { print("usage: uigif html setup.js step.js outdir n [w h scale wait]"); exit(2) }
let html = URL(fileURLWithPath: args[1])
let setup = (try? String(contentsOfFile: args[2], encoding: .utf8)) ?? ""
let step = (try? String(contentsOfFile: args[3], encoding: .utf8)) ?? ""
let outdir = args[4]
let n = Int(args[5])!
let w = args.count > 6 ? Double(args[6])! : 1072
let h = args.count > 7 ? Double(args[7])! : 652
let scale = args.count > 8 ? Double(args[8])! : 1
let wait = args.count > 9 ? Double(args[9])! : 1.5

let app = NSApplication.shared
app.setActivationPolicy(.prohibited)

class D: NSObject, WKNavigationDelegate, WKScriptMessageHandler {
  var i = 0
  func userContentController(_ u: WKUserContentController, didReceive m: WKScriptMessage) { print("[js] \(m.body)") }
  func frame(_ wv: WKWebView) {
    if i >= n { exit(0) }
    wv.evaluateJavaScript(step) { r, e in
      if let e = e { print("[step error] \(e)"); exit(1) }
      let cfg = WKSnapshotConfiguration()
      cfg.snapshotWidth = NSNumber(value: w * scale)
      wv.takeSnapshot(with: cfg) { img, err in
        guard let img = img, let tiff = img.tiffRepresentation,
              let rep = NSBitmapImageRep(data: tiff),
              let png = rep.representation(using: .png, properties: [:]) else {
          print("[snapshot error] \(String(describing: err))"); exit(1) }
        let out = String(format: "%@/f%03d.png", self.outdir_, self.i)
        try! png.write(to: URL(fileURLWithPath: out))
        self.i += 1
        self.frame(wv)
      }
    }
  }
  var outdir_ = ""
  func webView(_ wv: WKWebView, didFinish nav: WKNavigation!) {
    DispatchQueue.main.asyncAfter(deadline: .now() + wait) {
      wv.evaluateJavaScript(setup) { r, e in
        if let e = e { print("[setup error] \(e)"); exit(1) } else if let r = r { print("[setup] \(r)") }
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) { self.frame(wv) }
      }
    }
  }
}
let d = D(); d.outdir_ = outdir
let cfg = WKWebViewConfiguration()
cfg.userContentController.add(d, name: "log")
let pre = WKUserScript(source: "window.__log=function(s){window.webkit.messageHandlers.log.postMessage(String(s))};window.onerror=function(m,s,l){__log('ERR '+m+' @'+l)};if(!Element.prototype.setPointerCapture){Element.prototype.setPointerCapture=function(){};Element.prototype.releasePointerCapture=function(){}}", injectionTime: .atDocumentStart, forMainFrameOnly: true)
cfg.userContentController.addUserScript(pre)
let win = NSWindow(contentRect: NSRect(x: 0, y: 0, width: w, height: h), styleMask: [.borderless], backing: .buffered, defer: false)
let wv = WKWebView(frame: NSRect(x: 0, y: 0, width: w, height: h), configuration: cfg)
wv.navigationDelegate = d
win.contentView = wv
wv.loadFileURL(html, allowingReadAccessTo: html.deletingLastPathComponent().deletingLastPathComponent())
app.run()
