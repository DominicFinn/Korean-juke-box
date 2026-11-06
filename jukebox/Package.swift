// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "LofiJukebox",
    platforms: [.macOS(.v14)],
    targets: [
        .executableTarget(
            name: "LofiJukebox",
            path: "Sources/LofiJukebox",
            // Oreo and Milo, borrowed from Seoul Sisters
            resources: [.process("Resources")]
        ),
    ]
)
