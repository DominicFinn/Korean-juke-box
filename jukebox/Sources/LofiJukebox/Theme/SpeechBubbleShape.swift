import SwiftUI

/// A rounded manga speech bubble with a tail at the bottom, `tail` of the way across.
struct SpeechBubbleShape: Shape {
    var tail = 0.8

    func path(in rect: CGRect) -> Path {
        let body = CGRect(x: rect.minX, y: rect.minY, width: rect.width, height: rect.height - 16)
        let bubble = Path(roundedRect: body, cornerRadius: min(body.height / 2, 24), style: .continuous)

        let x = rect.minX + rect.width * tail
        var pointer = Path()
        pointer.move(to: CGPoint(x: x - 14, y: body.maxY - 4))
        pointer.addQuadCurve(to: CGPoint(x: x + 16, y: rect.maxY), control: CGPoint(x: x, y: body.maxY + 8))
        pointer.addQuadCurve(to: CGPoint(x: x + 6, y: body.maxY - 4), control: CGPoint(x: x + 9, y: body.maxY + 4))
        pointer.closeSubpath()
        return bubble.union(pointer)
    }
}
