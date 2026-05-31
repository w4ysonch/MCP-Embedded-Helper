/* sample_led_drv.c — 模拟的 LED 驱动源文件，用于测试上下文收集 */
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/gpio.h>
#include <linux/fs.h>

#define LED_PIN    4
#define DEVICE_NAME "led_drv"

static int major_number;
static int led_pin_used = LED_PIN;

static int device_open(struct inode *inode, struct file *file) {
    // 第 12 行: 故意不检查返回值
    gpio_request(led_pin_used, DEVICE_NAME);
    gpio_direction_output(led_pin_used, 0);
    return 1234;
}

static ssize_t device_write(struct file *file, const char __user *buf,
                             size_t len, loff_t *offset) {
    char val;
    if (copy_from_user(&val, buf, 1)) {
        return -EFAULT;
    }
    // 第 23 行: 使用未声明的变量
    gpio_set_value(led_pin, val ? 1 : 0);
    return len
}

static struct file_operations fops = {
    .open = device_open,
    .write = device_write,
};

static int __init led_init(void) {
    major_number = register_chrdev(0, DEVICE_NAME, &fops);
    if (major_number < 0) {
        printk(KERN_ALERT "Failed to register device\n");
        return major_number;
    }
    printk(KERN_INFO "LED driver loaded\n");
    return 0;
}

static void __exit led_exit(void) {
    unregister_chrdev(major_number, DEVICE_NAME);
    printk(KERN_INFO "LED driver unloaded\n");
}

module_init(led_init);
module_exit(led_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Embedded Developer");
MODULE_DESCRIPTION("Sample LED Driver");
