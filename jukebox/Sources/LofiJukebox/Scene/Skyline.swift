import SwiftUI

/// Two rows of tower blocks. `drawBlocks` paints the buildings and the windows that stay
/// lit, once. The things that blink and glow are handed to Core Animation as positions:
/// `flickeringWindows`, `warningLights` and `signs`.
enum Skyline {
    static func drawBlocks(_ context: inout GraphicsContext, layout: SceneLayout) {
        let rows = rows(for: layout)
        for building in rows.far {
            context.fill(Path(building.rect), with: .color(Palette.farCity))
        }
        windows(&context, in: rows.far, style: .far)

        for building in rows.near {
            context.fill(Path(building.rect), with: .color(Palette.nearCity))
            context.stroke(Path(building.rect), with: .color(Palette.ink), lineWidth: 2)
            if building.hasTank { waterTank(&context, on: building) }
            if building.hasAntenna { mast(&context, on: building) }
        }
        windows(&context, in: rows.near, style: .near)
    }

    static func rows(for layout: SceneLayout) -> (far: [Building], near: [Building]) {
        let ground = layout.sillTop + 4
        let width = layout.size.width
        let tall = layout.sillTop
        return (buildings(width: width, ground: ground, tall: tall, widths: 28...58, heights: 0.32...0.6, seed: 7),
                buildings(width: width, ground: ground, tall: tall, widths: 44...92, heights: 0.18...0.5, seed: 21))
    }

    /// The handful of windows that switch on and off every few seconds.
    static func flickeringWindows(in layout: SceneLayout) -> [FlickeringWindow] {
        let rows = rows(for: layout)
        var result: [FlickeringWindow] = []
        for (buildings, style) in [(rows.far, WindowStyle.far), (rows.near, WindowStyle.near)] {
            eachWindow(in: buildings, style: style) { rect, value, seed in
                if value > flickerThreshold {
                    result.append(FlickeringWindow(rect: rect, color: style.color, seed: seed))
                }
            }
        }
        return result
    }

    /// Tops of the masts, where the red aircraft lights go.
    static func warningLights(in layout: SceneLayout) -> [CGPoint] {
        rows(for: layout).near.filter(\.hasAntenna).map(mastTop)
    }

    static func signs(in layout: SceneLayout) -> [NeonPlacement] {
        let near = rows(for: layout).near
        let width = layout.size.width
        var result: [NeonPlacement] = []
        if let left = near.first(where: { $0.rect.height > 120 && $0.rect.midX > width * 0.06 && $0.rect.midX < width * 0.4 }) {
            result.append(NeonPlacement(text: "로파이", color: Palette.neonPink,
                                        origin: CGPoint(x: left.rect.maxX - 14, y: left.rect.minY + 12), floor: 0))
        }
        if let right = near.first(where: { $0.rect.height > 80 && $0.rect.midX > width * 0.55 && $0.rect.midX < width * 0.68 }) {
            result.append(NeonPlacement(text: "다방", color: Palette.neonTeal,
                                        origin: CGPoint(x: right.rect.minX - 6, y: right.rect.minY + 10), floor: 0.5))
        }
        return result
    }

    private static let flickerThreshold = 0.93

    private static func buildings(width: Double, ground: Double, tall: Double, widths: ClosedRange<Double>,
                                  heights: ClosedRange<Double>, seed: UInt64) -> [Building] {
        var random = SeededRandom(seed: seed)
        var result: [Building] = []
        var x = -8.0
        while x < width + 8 {
            let w = Double.random(in: widths, using: &random)
            let h = Double.random(in: heights, using: &random) * tall
            result.append(Building(
                rect: CGRect(x: x, y: ground - h, width: w, height: h),
                seed: random.next(),
                hasTank: Double.random(in: 0...1, using: &random) < 0.3,
                hasAntenna: Double.random(in: 0...1, using: &random) < 0.2
            ))
            x += w + Double.random(in: -6...3, using: &random)
        }
        return result
    }

    private enum WindowStyle {
        case far, near

        var cell: CGSize { self == .far ? CGSize(width: 8, height: 10) : CGSize(width: 11, height: 14) }
        var pane: CGSize { self == .far ? CGSize(width: 3, height: 4) : CGSize(width: 5, height: 7) }
        var lit: Double { self == .far ? 0.22 : 0.34 }
        var color: Color { self == .far ? Palette.lamp.opacity(0.45) : Palette.lamp }
    }

    private static func eachWindow(in buildings: [Building], style: WindowStyle,
                                   _ body: (CGRect, Double, UInt64) -> Void) {
        for building in buildings {
            let rect = building.rect.insetBy(dx: 5, dy: 6)
            var row: UInt64 = 0
            for y in stride(from: rect.minY, to: rect.maxY - style.pane.height, by: style.cell.height) {
                var column: UInt64 = 0
                for x in stride(from: rect.minX, to: rect.maxX - style.pane.width, by: style.cell.width) {
                    let value = SeededRandom.noise(building.seed, row, column)
                    let window = CGRect(x: x, y: y, width: style.pane.width, height: style.pane.height)
                    body(window, value, building.seed &+ row &* 977 &+ column)
                    column += 1
                }
                row += 1
            }
        }
    }

    /// The windows that are always on: warm lamps, and the odd blue TV glow.
    private static func windows(_ context: inout GraphicsContext, in buildings: [Building], style: WindowStyle) {
        var warm = Path()
        var screens = Path()
        eachWindow(in: buildings, style: style) { rect, value, _ in
            guard value < style.lit else { return }
            if value < 0.03 { screens.addRect(rect) } else { warm.addRect(rect) }
        }
        context.fill(warm, with: .color(style.color))
        context.fill(screens, with: .color(Palette.screenGlow.opacity(0.8)))
    }

    private static func waterTank(_ context: inout GraphicsContext, on building: Building) {
        let r = building.rect
        let tank = CGRect(x: r.minX + r.width * 0.25, y: r.minY - 14, width: 16, height: 10)
        var legs = Path()
        legs.move(to: CGPoint(x: tank.minX + 3, y: tank.maxY))
        legs.addLine(to: CGPoint(x: tank.minX + 3, y: r.minY))
        legs.move(to: CGPoint(x: tank.maxX - 3, y: tank.maxY))
        legs.addLine(to: CGPoint(x: tank.maxX - 3, y: r.minY))
        context.stroke(legs, with: .color(Palette.ink), lineWidth: 2)
        context.fill(Path(roundedRect: tank, cornerRadius: 3), with: .color(Palette.nearCity))
        context.stroke(Path(roundedRect: tank, cornerRadius: 3), with: .color(Palette.ink), lineWidth: 2)
    }

    private static func mastTop(of building: Building) -> CGPoint {
        CGPoint(x: building.rect.maxX - 10, y: building.rect.minY - 26)
    }

    private static func mast(_ context: inout GraphicsContext, on building: Building) {
        let top = mastTop(of: building)
        var mast = Path()
        mast.move(to: CGPoint(x: top.x, y: building.rect.minY))
        mast.addLine(to: top)
        mast.move(to: CGPoint(x: top.x - 5, y: top.y + 8))
        mast.addLine(to: CGPoint(x: top.x + 5, y: top.y + 8))
        context.stroke(mast, with: .color(Palette.ink), lineWidth: 2)
        context.fill(Path(ellipseIn: CGRect(x: top.x - 2.5, y: top.y - 2.5, width: 5, height: 5)),
                     with: .color(Palette.ink))
    }
}
