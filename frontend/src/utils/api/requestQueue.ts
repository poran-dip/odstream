/**
 * Runs async requests one at a time, in the order they were added.
 *
 * Used so that, e.g., rapid start/stop clicks reach the backend in order
 * instead of racing each other.
 */
export class RequestQueue {
  private queue: Array<() => Promise<unknown>> = [];
  private processing = false;

  async add<T>(request: () => Promise<T>): Promise<T> {
    return new Promise((resolve, reject) => {
      this.queue.push(async () => {
        try {
          const result = await request();
          resolve(result);
        } catch (error) {
          reject(error);
        }
      });
      this.process();
    });
  }

  private async process() {
    if (this.processing || this.queue.length === 0) return;

    this.processing = true;
    while (this.queue.length > 0) {
      const request = this.queue.shift()!;
      await request();
    }
    this.processing = false;
  }
}
