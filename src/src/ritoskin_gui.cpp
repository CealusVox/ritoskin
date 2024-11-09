/*
 * Copyright (c) 2024 nylish
 * All rights reserved.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <https://www.gnu.org/licenses/>.
 */

#include <QApplication>
#include <QMainWindow>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QPushButton>
#include <QTextEdit>
#include <QLineEdit>
#include <QProcess>
#include <QFileInfo>
#include <QMessageBox>
#include <QDir>

class MainWindow : public QMainWindow {
    Q_OBJECT

public:
    MainWindow(QWidget *parent = nullptr) : QMainWindow(parent) {
        setWindowTitle("RitoSkin");
        setGeometry(100, 100, 800, 600);

        QWidget *centralWidget = new QWidget(this);
        QVBoxLayout *layout = new QVBoxLayout(centralWidget);
        setCentralWidget(centralWidget);

        terminalOutput = new QTextEdit(this);
        terminalOutput->setReadOnly(true);
        layout->addWidget(terminalOutput);

        inputLine = new QLineEdit(this);
        inputLine->setPlaceholderText("Enter input here...");
        inputLine->setEnabled(false);
        layout->addWidget(inputLine);

        QHBoxLayout *buttonLayout = new QHBoxLayout();
        layout->addLayout(buttonLayout);

        deleteFolderButton = new QPushButton("Delete Images Folder", this);
        buttonLayout->addWidget(deleteFolderButton);

        runProgramButton = new QPushButton("Run RitoSkin", this);
        buttonLayout->addWidget(runProgramButton);

        runExtractorButton = new QPushButton("Run RitoSkin Extractor", this);
        buttonLayout->addWidget(runExtractorButton);

        scrapLoadingScreenButton = new QPushButton("Scrap Loading Screen", this);
        buttonLayout->addWidget(scrapLoadingScreenButton);

        process = new QProcess(this);
        connect(process, &QProcess::readyReadStandardOutput, this, &MainWindow::handleStdout);
        connect(process, &QProcess::readyReadStandardError, this, &MainWindow::handleStderr);
        connect(process, QOverload<int, QProcess::ExitStatus>::of(&QProcess::finished),
                this, &MainWindow::handleFinished);

        connect(deleteFolderButton, &QPushButton::clicked, this, &MainWindow::deleteFolder);
        connect(runProgramButton, &QPushButton::clicked, this, &MainWindow::runRitoSkin);
        connect(runExtractorButton, &QPushButton::clicked, this, &MainWindow::runRitoSkinExtractor);
        connect(scrapLoadingScreenButton, &QPushButton::clicked, this, &MainWindow::scrapLoadingScreen);
        connect(inputLine, &QLineEdit::returnPressed, this, &MainWindow::sendInput);
    }

private slots:
    void deleteFolder() {
        QDir dir("images");
        if (dir.exists()) {
            if (dir.removeRecursively()) {
                terminalOutput->append("Deleted 'images' folder.");
            } else {
                terminalOutput->append("Error deleting 'images' folder.");
            }
        } else {
            terminalOutput->append("'images' folder not found.");
        }
    }

    void runRitoSkin() {
        runProgram("ritoskin.exe");
    }

    void runRitoSkinExtractor() {
        runProgram("ritoskin_extractor.exe");
    }

    void scrapLoadingScreen() {
        QFileInfo checkFile("resources/scrap_tex_to_dds.py");
        if (checkFile.exists() && checkFile.isFile()) {
            terminalOutput->append("Starting to scrape loading screen...");
            scrapLoadingScreenButton->setEnabled(false);
            process->start("resources/scrap_tex_to_dds.py");
        } else {
            terminalOutput->append("Error: scrap_tex_to_dds.py not found.");
        }
    }

    void handleStdout() {
        QByteArray data = process->readAllStandardOutput();
        terminalOutput->append(QString::fromUtf8(data).trimmed());
    }

    void handleStderr() {
        QByteArray data = process->readAllStandardError();
        terminalOutput->append("Error: " + QString::fromUtf8(data).trimmed());
    }

    void handleFinished(int exitCode, QProcess::ExitStatus exitStatus) {
        if (exitStatus == QProcess::NormalExit) {
            terminalOutput->append("Program finished successfully.");
        } else {
            terminalOutput->append("Program crashed or was killed. Exit code: " + QString::number(exitCode));
        }
        runProgramButton->setEnabled(true);
        runExtractorButton->setEnabled(true);
        scrapLoadingScreenButton->setEnabled(true);
        inputLine->setEnabled(false);
    }

    void sendInput() {
        QString text = inputLine->text();
        if (!text.isEmpty()) {
            process->write((text + "\n").toUtf8());
            terminalOutput->append("> " + text);
            inputLine->clear();
        }
    }

private:
    void runProgram(const QString &program) {
        QFileInfo checkFile(program);
        if (checkFile.exists() && checkFile.isFile()) {
            process->start(program);
            runProgramButton->setEnabled(false);
            runExtractorButton->setEnabled(false);
            inputLine->setEnabled(true);
            inputLine->setFocus();
        } else {
            terminalOutput->append("Error: " + program + " not found.");
        }
    }

    QTextEdit *terminalOutput;
    QLineEdit *inputLine;
    QPushButton *deleteFolderButton;
    QPushButton *runProgramButton;
    QPushButton *runExtractorButton;
    QPushButton *scrapLoadingScreenButton;
    QProcess *process;
};

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);
    MainWindow window;
    window.show();
    return app.exec();
}

#include "main.moc"