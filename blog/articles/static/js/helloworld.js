"use strict";

// Массив учебных данных для лабораторной работы № 7.
var groupmates = [
    { name: "Анна", surname: "Соколова", group: "ПИС-24-1", marks: [5, 4, 5] },
    { name: "Илья", surname: "Морозов", group: "ПИС-24-1", marks: [4, 4, 5] },
    { name: "Мария", surname: "Кузнецова", group: "ПИС-24-2", marks: [5, 5, 5] },
    { name: "Дмитрий", surname: "Волков", group: "ПИС-24-2", marks: [3, 4, 4] },
    { name: "Екатерина", surname: "Попова", group: "ПИС-24-1", marks: [5, 5, 4] },
    { name: "Артём", surname: "Лебедев", group: "ПИС-24-3", marks: [3, 4, 3] }
];

console.log("Hello, world!");
console.log("Массив groupmates:", groupmates);

// Дополняет строку пробелами справа до заданной ширины.
var rpad = function (str, length) {
    str = String(str);
    while (str.length < length) {
        str += " ";
    }
    return str;
};

var averageMark = function (student) {
    if (!student.marks || student.marks.length === 0) {
        return 0;
    }
    var sum = student.marks.reduce(function (total, mark) {
        return total + Number(mark);
    }, 0);
    return sum / student.marks.length;
};

var printStudents = function (students) {
    console.log(
        rpad("Имя", 15) +
        rpad("Фамилия", 18) +
        rpad("Группа", 12) +
        rpad("Оценки", 18) +
        "Средний балл"
    );
    console.log("-".repeat(76));
    for (var i = 0; i < students.length; i++) {
        console.log(
            rpad(students[i].name, 15) +
            rpad(students[i].surname, 18) +
            rpad(students[i].group, 12) +
            rpad(students[i].marks.join(", "), 18) +
            averageMark(students[i]).toFixed(2)
        );
    }
    console.log("\n");
};

var filterStudentsByGroup = function (students, groupName) {
    var normalizedGroup = String(groupName).trim().toLocaleLowerCase("ru-RU");
    if (!normalizedGroup) {
        return [];
    }
    return students.filter(function (student) {
        return student.group.toLocaleLowerCase("ru-RU") === normalizedGroup;
    });
};

var filterStudentsByAverage = function (students, threshold) {
    return students.filter(function (student) {
        return averageMark(student) > threshold;
    });
};

var resultsBody = document.getElementById("student-results");
var statusText = document.getElementById("student-filter-status");

var renderStudents = function (students, description) {
    if (!resultsBody || !statusText) {
        return;
    }
    resultsBody.replaceChildren();
    statusText.textContent = description + " Найдено студентов: " + students.length + ".";

    if (students.length === 0) {
        var emptyRow = document.createElement("tr");
        var emptyCell = document.createElement("td");
        emptyCell.colSpan = 5;
        emptyCell.textContent = "По заданным условиям студенты не найдены.";
        emptyRow.appendChild(emptyCell);
        resultsBody.appendChild(emptyRow);
    } else {
        students.forEach(function (student) {
            var row = document.createElement("tr");
            [
                student.name,
                student.surname,
                student.group,
                student.marks.join(", "),
                averageMark(student).toFixed(2)
            ].forEach(function (value) {
                var cell = document.createElement("td");
                cell.textContent = value;
                row.appendChild(cell);
            });
            resultsBody.appendChild(row);
        });
    }

    console.log(description);
    printStudents(students);
};

var groupFilterButton = document.getElementById("group-filter-button");
var groupFilterInput = document.getElementById("group-filter-input");
if (groupFilterButton && groupFilterInput) {
    groupFilterButton.addEventListener("click", function () {
        var groupName = groupFilterInput.value;
        if (!groupName.trim()) {
            statusText.textContent = "Введите название группы для фильтрации.";
            groupFilterInput.focus();
            return;
        }
        renderStudents(filterStudentsByGroup(groupmates, groupName), "Фильтр по группе: " + groupName.trim() + ".");
    });
}

var averageFilterButton = document.getElementById("average-filter-button");
var averageFilterInput = document.getElementById("average-filter-input");
if (averageFilterButton && averageFilterInput) {
    averageFilterButton.addEventListener("click", function () {
        if (averageFilterInput.value.trim() === "") {
            statusText.textContent = "Введите порог среднего балла от 1 до 5.";
            averageFilterInput.focus();
            return;
        }
        var threshold = Number(averageFilterInput.value);
        if (!Number.isFinite(threshold) || threshold < 1 || threshold > 5) {
            statusText.textContent = "Порог должен быть числом от 1 до 5.";
            averageFilterInput.focus();
            return;
        }
        renderStudents(
            filterStudentsByAverage(groupmates, threshold),
            "Студенты со средним баллом выше " + threshold + "."
        );
    });
}

var showAllButton = document.getElementById("show-all-students-button");
if (showAllButton) {
    showAllButton.addEventListener("click", function () {
        renderStudents(groupmates, "Полный список студентов.");
    });
}

printStudents(groupmates);
renderStudents(groupmates, "Показаны все студенты.");
