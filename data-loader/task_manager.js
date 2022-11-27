class TaskManager {
  constructor(max_task_count = 2, onDone) {
    this.max_task_count = max_task_count;
    this.running_count = 0;
    this.tasks = [];
    this.onDone = onDone;
  }

  check() {
    if (this.running_count >= this.max_task_count) return;

    if (this.tasks.length) {
      this.tasks.shift()();
      this.running_count++;
    }

    if (this.running_count === 0 && this.onDone) this.onDone();
  }

  addTask(f) {
    const task = async () => {
      await f().catch(console.error);
      this.running_count--;
      this.check();
    };

    this.tasks.push(task);
    this.check();
  }
}

exports.TaskManager = TaskManager;
