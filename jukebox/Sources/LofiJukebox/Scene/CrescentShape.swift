import SwiftUI

struct CrescentShape: Shape {
    func path(in rect: CGRect) -> Path {
        let moon = Path(ellipseIn: rect)
        let bite = Path(ellipseIn: rect.offsetBy(dx: rect.width * 0.34, dy: -rect.height * 0.14))
        return moon.subtracting(bite)
    }
}
