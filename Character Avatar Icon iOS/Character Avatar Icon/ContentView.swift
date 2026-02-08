//
//  ContentView.swift
//  Character Avatar Icon
//
//  Created by David Marchenko on 2/8/26.
//

import SwiftUI

// MARK: - Sample Character Data

struct SampleCharacter {
    let name: String
    let imageName: String
    let imageSize: CGSize
    let headBoundingBox: HeadBoundingBox

    static let fox = SampleCharacter(
        name: "Fox",
        imageName: "Fox",
        imageSize: CGSize(width: 1536, height: 2752),
        headBoundingBox: HeadBoundingBox(x1: 586, y1: 21, x2: 1014, y2: 547)
    )

    static let kirby = SampleCharacter(
        name: "Kirby",
        imageName: "Kirby",
        imageSize: CGSize(width: 1439, height: 1333),
        headBoundingBox: HeadBoundingBox(x1: 92, y1: 1, x2: 1286, y2: 1197)
    )

    static let frankie = SampleCharacter(
        name: "Frankie",
        imageName: "Frankie",
        imageSize: CGSize(width: 1091, height: 1953),
        headBoundingBox: HeadBoundingBox(x1: 407, y1: 105, x2: 686, y2: 510)
    )

    static let trainerRex = SampleCharacter(
        name: "Trainer Rex",
        imageName: "TrainerRex",
        imageSize: CGSize(width: 960, height: 1440),
        headBoundingBox: HeadBoundingBox(x1: 372, y1: 62, x2: 598, y2: 307)
    )

    static let all: [SampleCharacter] = [.fox, .kirby, .frankie, .trainerRex]
}

// MARK: - Content View

struct ContentView: View {
    var body: some View {
        ScrollView {
            VStack(spacing: 32) {
                Text("Avatar Icon Demo")
                    .font(.largeTitle)
                    .fontWeight(.bold)

                // MARK: - All Characters with Auto-framing
                VStack(spacing: 16) {
                    Text("Auto-framing with Real Characters")
                        .font(.headline)
                    Text("Each character uses head bounding box for positioning")
                        .font(.caption)
                        .foregroundStyle(.secondary)

                    LazyVGrid(columns: [
                        GridItem(.flexible()),
                        GridItem(.flexible())
                    ], spacing: 16) {
                        ForEach(SampleCharacter.all, id: \.name) { character in
                            VStack {
                                AvatarIcon(
                                    characterImage: Image(character.imageName),
                                    imageSize: character.imageSize,
                                    headBoundingBox: character.headBoundingBox,
                                    fill: .orange
                                )
                                .frame(width: 136, height: 160)

                                Text(character.name)
                                    .font(.caption)
                            }
                        }
                    }
                }

                Divider()

                // MARK: - Gradient Variants for One Character
                VStack(spacing: 16) {
                    Text("Gradient Variants")
                        .font(.headline)

                    HStack(spacing: 12) {
                        ForEach([
                            ("Orange", AvatarFill.orange),
                            ("Blue", AvatarFill.blue),
                            ("Green", AvatarFill.green),
                            ("Purple", AvatarFill.purple),
                        ], id: \.0) { name, fill in
                            VStack {
                                AvatarIcon(
                                    characterImage: Image(SampleCharacter.frankie.imageName),
                                    imageSize: SampleCharacter.frankie.imageSize,
                                    headBoundingBox: SampleCharacter.frankie.headBoundingBox,
                                    fill: fill
                                )
                                .frame(width: 68, height: 80)

                                Text(name)
                                    .font(.caption2)
                            }
                        }
                    }
                }

                Divider()

                // MARK: - Size Comparison
                VStack(spacing: 16) {
                    Text("Responsive Sizing")
                        .font(.headline)

                    HStack(alignment: .bottom, spacing: 16) {
                        VStack {
                            AvatarIcon(
                                characterImage: Image(SampleCharacter.kirby.imageName),
                                imageSize: SampleCharacter.kirby.imageSize,
                                headBoundingBox: SampleCharacter.kirby.headBoundingBox,
                                fill: .blue
                            )
                            .frame(width: 51, height: 60)
                            Text("60pt")
                                .font(.caption2)
                        }

                        VStack {
                            AvatarIcon(
                                characterImage: Image(SampleCharacter.kirby.imageName),
                                imageSize: SampleCharacter.kirby.imageSize,
                                headBoundingBox: SampleCharacter.kirby.headBoundingBox,
                                fill: .green
                            )
                            .frame(width: 85, height: 100)
                            Text("100pt")
                                .font(.caption2)
                        }

                        VStack {
                            AvatarIcon(
                                characterImage: Image(SampleCharacter.kirby.imageName),
                                imageSize: SampleCharacter.kirby.imageSize,
                                headBoundingBox: SampleCharacter.kirby.headBoundingBox,
                                fill: .purple
                            )
                            .frame(width: 136, height: 160)
                            Text("160pt")
                                .font(.caption2)
                        }
                    }
                }
            }
            .padding()
        }
    }
}

#Preview {
    ContentView()
}
