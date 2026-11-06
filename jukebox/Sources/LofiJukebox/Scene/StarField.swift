import SwiftUI

/// Four-point manga sparkles scattered over the sky, clear of the moon and the buildings.
enum StarField {
    static func stars(in layout: SceneLayout) -> [Twinkle] {
        var random = SeededRandom(seed: 3)
        let size = layout.size
        let rows = Skyline.rows(for: layout)
        let buildings = (rows.far + rows.near).map { $0.rect.insetBy(dx: -4, dy: -30) }
        var result: [Twinkle] = []
        for _ in 0..<18 {
            let point = CGPoint(x: Double.random(in: 0.03...0.97, using: &random) * size.width,
                                y: Double.random(in: 0.05...0.42, using: &random) * size.height)
            let speed = Double.random(in: 0.6...1.8, using: &random)
            let phase = Double.random(in: 0...(2 * .pi), using: &random)
            let radius = Double.random(in: 2...5, using: &random)
            guard hypot(point.x - layout.moon.x, point.y - layout.moon.y) > 45,
                  !buildings.contains(where: { $0.contains(point) }) else { continue }
            result.append(Twinkle(point: point, radius: radius, speed: speed, phase: phase))
        }
        return result
    }

    /// Curves pinched into the centre give the classic manga sparkle.
    static func sparkle(at p: CGPoint, radius r: Double) -> Path {
        var path = Path()
        path.move(to: CGPoint(x: p.x, y: p.y - r))
        path.addQuadCurve(to: CGPoint(x: p.x + r, y: p.y), control: p)
        path.addQuadCurve(to: CGPoint(x: p.x, y: p.y + r), control: p)
        path.addQuadCurve(to: CGPoint(x: p.x - r, y: p.y), control: p)
        path.addQuadCurve(to: CGPoint(x: p.x, y: p.y - r), control: p)
        return path
    }
}
