// uiprobe: load an HTML file in an offscreen WKWebView, run a probe script, snapshot to PNG.
//   uiprobe <html> <probe.js> <out.png> [width height scale waitSeconds]
import Cocoa
import WebKit

let args = CommandLine.arguments
guard args.count >= 4 else { print("usage: uiprobe html probe.js out.png [w h scale wait]"); exit(2) }
let html = URL(fileURLWithPath: args[1])
let probe = (try? String(contentsOfFile: args[2], encoding: .utf8)) ?? ""
let out = args[3]
let w = args.count > 4 ? Double(args[4])! : 1072
let h = args.count > 5 ? Double(args[5])! : 652
let scale = args.count > 6 ? Double(args[6])! : 2
let wait = args.count > 7 ? Double(args[7])! : 1.5

let app = NSApplication.shared
app.setActivationPolicy(.prohibited)

class D: NSObject, WKNavigationDelegate, WKScriptMessageHandler {
  func userContentController(_ u: WKUserContentController, didReceive m: WKScriptMessage) { print("[js] \(m.body)") }
  func webView(_ wv: WKWebView, didFinish nav: WKNavigation!) {
    DispatchQueue.main.asyncAfter(deadline: .now() + wait) {
      wv.evaluateJavaScript(probe) { r, e in
        if let e = e { print("[probe error] \(e)") } else if let r = r { print("[probe] \(r)") }
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
          let cfg = WKSnapshotConfiguration()
          cfg.snapshotWidth = NSNumber(value: w * scale)
          wv.takeSnapshot(with: cfg) { img, err in
            guard let img = img, let tiff = img.tiffRepresentation,
                  let rep = NSBitmapImageRep(data: tiff),
                  let png = rep.representation(using: .png, properties: [:]) else {
              print("[snapshot error] \(String(describing: err))"); exit(1) }
            try! png.write(to: URL(fileURLWithPath: out))
            print("wrote \(out) \(rep.pixelsWide)x\(rep.pixelsHigh)")
            exit(0)
          }
        }
      }
    }
  }
}
let d = D()
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
