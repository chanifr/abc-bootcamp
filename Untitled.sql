CREATE TABLE `users` (
  `id` varchar(36) PRIMARY KEY COMMENT 'UUID',
  `email` varchar(255) UNIQUE NOT NULL COMMENT 'Indexed',
  `hashed_password` varchar(255) NOT NULL,
  `full_name` varchar(255) NOT NULL,
  `role` varchar(20) NOT NULL DEFAULT 'read_only' COMMENT 'Enum: read_only, editor, admin',
  `is_active` boolean NOT NULL DEFAULT true,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL
);

CREATE TABLE `candidates` (
  `id` varchar(36) PRIMARY KEY COMMENT 'UUID',
  `name` varchar(255) NOT NULL,
  `email` varchar(255) UNIQUE NOT NULL COMMENT 'Indexed',
  `phone` varchar(50) NOT NULL,
  `location` varchar(255) NOT NULL,
  `summary` text NOT NULL,
  `status` varchar(20) NOT NULL DEFAULT 'Active' COMMENT 'Enum: Active, Hired, Rejected, Withdrawn',
  `sort_order` integer NOT NULL DEFAULT 0,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL
);

CREATE TABLE `positions` (
  `id` varchar(36) PRIMARY KEY COMMENT 'UUID',
  `title` varchar(255) NOT NULL,
  `department` varchar(255) NOT NULL,
  `location` varchar(255) NOT NULL,
  `description` text NOT NULL,
  `requirements` text NOT NULL,
  `min_experience_years` integer NOT NULL,
  `status` varchar(20) NOT NULL DEFAULT 'Open' COMMENT 'Enum: Open, Closed, On Hold',
  `posted_date` date NOT NULL,
  `sort_order` integer NOT NULL DEFAULT 0,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL
);

CREATE TABLE `experiences` (
  `id` varchar(36) PRIMARY KEY COMMENT 'UUID',
  `candidate_id` varchar(36) NOT NULL,
  `company` varchar(255) NOT NULL,
  `title` varchar(255) NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date COMMENT 'NULL means current position',
  `description` text NOT NULL
);

CREATE TABLE `education` (
  `id` varchar(36) PRIMARY KEY COMMENT 'UUID',
  `candidate_id` varchar(36) NOT NULL,
  `institution` varchar(255) NOT NULL,
  `degree` varchar(255) NOT NULL,
  `field` varchar(255) NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date COMMENT 'NULL means ongoing'
);

CREATE TABLE `skills` (
  `id` varchar(36) PRIMARY KEY COMMENT 'UUID',
  `candidate_id` varchar(36) NOT NULL,
  `name` varchar(255) NOT NULL,
  `level` varchar(20) NOT NULL COMMENT 'Enum: Beginner, Intermediate, Advanced, Expert'
);

CREATE TABLE `documents` (
  `id` varchar(36) PRIMARY KEY COMMENT 'UUID',
  `candidate_id` varchar(36) NOT NULL,
  `type` varchar(20) NOT NULL COMMENT 'Enum: CV, Cover Letter, Certificate, Other',
  `name` varchar(255) NOT NULL,
  `url` varchar(512) NOT NULL,
  `uploaded_at` datetime NOT NULL
);

CREATE TABLE `position_skills` (
  `id` varchar(36) PRIMARY KEY COMMENT 'UUID',
  `position_id` varchar(36) NOT NULL,
  `name` varchar(255) NOT NULL COMMENT 'Required skill for the position'
);

CREATE TABLE `candidate_positions` (
  `id` varchar(36) PRIMARY KEY COMMENT 'UUID',
  `candidate_id` varchar(36) NOT NULL,
  `position_id` varchar(36) NOT NULL,
  `applied_at` datetime NOT NULL
);

CREATE UNIQUE INDEX `uq_candidate_position` ON `candidate_positions` (`candidate_id`, `position_id`);

ALTER TABLE `experiences` ADD FOREIGN KEY (`candidate_id`) REFERENCES `candidates` (`id`) ON DELETE CASCADE;

ALTER TABLE `education` ADD FOREIGN KEY (`candidate_id`) REFERENCES `candidates` (`id`) ON DELETE CASCADE;

ALTER TABLE `skills` ADD FOREIGN KEY (`candidate_id`) REFERENCES `candidates` (`id`) ON DELETE CASCADE;

ALTER TABLE `documents` ADD FOREIGN KEY (`candidate_id`) REFERENCES `candidates` (`id`) ON DELETE CASCADE;

ALTER TABLE `position_skills` ADD FOREIGN KEY (`position_id`) REFERENCES `positions` (`id`) ON DELETE CASCADE;

ALTER TABLE `candidate_positions` ADD FOREIGN KEY (`candidate_id`) REFERENCES `candidates` (`id`) ON DELETE CASCADE;

ALTER TABLE `candidate_positions` ADD FOREIGN KEY (`position_id`) REFERENCES `positions` (`id`) ON DELETE CASCADE;
