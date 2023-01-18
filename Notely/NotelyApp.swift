//
//  NotelyApp.swift
//  Notely
//
//  Created by paul on 18/01/2023.
//

import SwiftUI

@main
struct NotelyApp: App {
    let persistenceController = PersistenceController.shared

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(\.managedObjectContext, persistenceController.container.viewContext)
        }
    }
}
