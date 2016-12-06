#path <- "D:/multiagent projects/python.ace/ace/output.csv"

path <- "C:/Users/d.omelianchyk/PycharmProjects/ace/output.csv"

table <- read.csv(path, stringsAsFactors = FALSE, row.names = NULL, sep = ";", dec = ".")

table$step <- factor(table$step)

table$inverse.sold <- 1/table$sold
table[table$inverse.sold == 'Inf' | table$inverse.sold == 'NaN', 'inverse.sold' ] <- NA

require(ggplot2)

table$step <- as.integer(table$step)

ggplot(table[table$step < 100,], aes(x = price, y = sold)) + geom_point(aes(colour = step))

ggplot(table, aes(x = price, y = sold)) + geom_point() + 
  stat_smooth() + theme_bw()

ggplot(table, aes(x = salary, y = workers)) + geom_point(aes(colour = step)) + 
  stat_smooth() + theme_bw()

ggplot(table[table$firm_type == 'Unknown' & table$salary > 1000,], aes(x = salary, y = workers)) + geom_point(aes(colour = step)) + 
  stat_smooth() + theme_bw()

fit <- lm(price ~ inverse.sold, table)

table$px <- table$workers * 10
table$ax <- 10/table$salary

require(reshape2)
require(data.table)

table_melt <- melt(table[ c('firm_id', 'step', 'px', 'ax')], id.vars = c('firm_id', 'step'))

table_melt_11 <- table_melt[table$firm_id == '11',]

ggplot(table_melt, aes(x = step, y = value)) + 
  geom_line(aes(color = factor(variable)), stat = 'identity')

test <- split(table, table$firm_id)

get.mx <- function(x) {
  Q <- x[order(x[, 'step']),]
  Q[, 'mx'] <- c(0, 10 * diff(Q[, 'workers'])/diff(Q[, 'workers'] * Q[, 'salary']))
  Q
}

table.with.mx <- as.data.frame(rbindlist(lapply(test, get.mx)))
table.with.mx[table.with.mx$mx == 'Inf', 'mx'] <- NA

table.with.mx$firm_id <- as.numeric(table.with.mx$firm_id)

ggplot(table.with.mx, aes(x = step, y = mx)) + geom_point()

table_melt <- melt(table.with.mx[, c('firm_id', 'step', 'ax', 'mx')], id.vars = c('firm_id', 'step'))

ggplot(table_melt, aes(x = step, y = value, 
          group = variable)) + geom_point(aes(colour = variable)) + stat_smooth()

table_melt <- melt(table[, c('firm_id', 'step', 'sold', 'price', 'product_supply')],
                   id.vars = c('firm_id', 'price', 'step'))

table_melt$price <- as.numeric(table_melt$price)
table_melt$value <- as.numeric(table_melt$value)

ggplot(table_melt, aes(x = price, y = value, group = variable)) +
         geom_point(aes(colour = variable)) + stat_smooth()

require(dplyr)
require(plyr)

totals <- ddply(table, 'step', summarise, total_sold = sum(sold * price), 
                total_supply = sum(product_supply * price), quantity= sum(sold))
                
                

totals$demand <- 100000

totals_melt <- melt(totals, id.vars = 'step')

ggplot(totals_melt, aes(x = as.numeric(step), 
          y = value, group = variable)) + geom_line(aes(color = variable))
