resource "aws_lb" "my_app_lb" {
  name               = "my-app-lb-2"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.sg_alb_internet.id]
  subnets            = [aws_subnet.public.id, aws_subnet.public_2.id]
  enable_deletion_protection = false
}

resource "aws_lb_target_group" "my_app_lb_tg" {
  name     = "my-app-lb-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id
  target_type = "instance"
  health_check {
    path                = "/health"
    protocol            = "HTTP"
    port                = "traffic-port"
    interval            = 60
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }
}

resource "aws_lb_listener" "my_app_listener" {
  load_balancer_arn = aws_lb.my_app_lb.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.my_app_lb_tg.arn
    }
}


resource "aws_lb_target_group_attachment" "instance_attachment" {
  # covert a list of instance objects to a map with instance ID as the key, and an instance
  # object as the value.
  for_each = {
    for k, v in aws_instance.app_server :
    k => v
  }

  target_group_arn = aws_lb_target_group.my_app_lb_tg.arn
  target_id        = each.value.id
  port             = 8000
}